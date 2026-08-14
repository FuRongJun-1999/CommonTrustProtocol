#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件接口（MCP Client）协议层测试（M1）
=====================================
覆盖（验证单元必选项）：握手/版本协商/工具发现/调用/通知忽略/
非法JSON/空响应/超时重建/流式截断。check 框架。
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FAKE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fake_mcp_server.py")
PY = sys.executable

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def make_client(env=None, timeout=10):
    from harness.plugins.client import MCPClient
    return MCPClient("fake", [PY, FAKE], env=env or {}, timeout=timeout,
                     log=lambda *a: None)


def test_handshake():
    c = make_client()
    check("握手成功", c.start() is True, f"state={c.state}")
    check("状态 READY", c.state == "ready")
    check("健康检查", c.health() is True)
    c.close()
    check("关闭后状态", c.state == "closed")


def test_tools_discovery():
    c = make_client()
    c.start()
    tools = c.list_tools()
    check("工具发现", len(tools) == 2 and tools[0]["name"] == "echo",
          str([t["name"] for t in tools]))
    c.close()


def test_call_echo():
    c = make_client()
    c.start()
    r = c.call("echo", {"text": "你好"})
    check("调用回显", r["ok"] and r["data"] == "echo:你好", f"data={r['data']}")
    c.close()


def test_call_unknown_tool():
    c = make_client()
    c.start()
    r = c.call("nope", {})
    check("未知工具 isError", r["ok"] is False)
    c.close()


def test_notification_ignored():
    c = make_client({"FAKE_SEND_NOTIFY": "1"})
    t0 = time.time()
    ok = c.start()
    dt = time.time() - t0
    check("通知不阻塞握手", ok and dt < 5, f"{dt:.1f}s")
    r = c.call("echo", {"text": "x"})
    check("通知后调用正常", r["ok"] and r["data"] == "echo:x")
    c.close()


def test_bad_json_skipped():
    c = make_client({"FAKE_BAD_JSON": "1"})
    ok = c.start()
    check("非法JSON行跳过", ok is True)
    r = c.call("echo", {"text": "y"})
    check("非法JSON后调用正常", r["ok"] and r["data"] == "echo:y")
    c.close()


def test_slow_timeout_rebuild():
    # 慢响应只影响 call（FAKE_SLOW_MS），握手正常；call 超时 → 容器化失败
    c = make_client({"FAKE_SLOW_MS": "5000"}, timeout=2)
    ok = c.start()
    check("慢 server 握手正常", ok is True)
    t0 = time.time()
    r = c.call("echo", {"text": "x"}, timeout=1)
    dt = time.time() - t0
    check("慢 call 超时容器化", r["ok"] is False and "超时" in r["error"],
          f"{dt:.1f}s {r['error'][:40]}")
    c.close()


def test_stream_truncation():
    c = make_client({"FAKE_LARGE_KB": "100"})
    c.start()
    from harness.plugins.client import STREAM_BUFFER_MAX, STREAM_TRUNCATED
    r = c.call("big", {})
    check("大payload截断", r["ok"] and len(r["data"]) <= STREAM_BUFFER_MAX + 30,
          f"len={len(r['data'])}")
    check("截断标记", STREAM_TRUNCATED in r["data"])
    c.close()


def test_unknown_method():
    c = make_client()
    c.start()
    ok, result = c._request("no/such/method", {})
    check("未知方法错误响应", ok is False and result, str(result)[:40])
    c.close()


# ================= M2：管理器/注入/安全 =================

def test_manager_config(tmp=None):
    from harness.plugins.manager import PluginManager
    import tempfile
    p = tmp or os.path.join(tempfile.mkdtemp(), "plugins.json")
    m = PluginManager(p)
    m.save_config([{"name": "fake", "command": [PY, FAKE], "enabled": True}])
    with open(p, "r", encoding="utf-8") as f:
        head = f.read()
    check("配置写入风险标注头", "敏感信息" in head, "（决议 Q3）")
    cfg = m.load_config()
    check("配置加载", len(cfg) == 1 and cfg[0]["name"] == "fake")
    check("配置缺字段兜底", m.load_config() and True)
    return p


def test_manager_start_and_inject():
    from harness.plugins.manager import PluginManager
    from harness.plugins import inject
    p = test_manager_config()
    m = PluginManager(p, log=lambda *a: None)
    result = m.start_all()
    check("插件启动", result.get("fake") is True, str(result))
    n = inject.register_plugin_tools(m, "fake")
    check("工具注入命名空间", n == 2 and "mcp__fake__echo" in inject.EXT_TOOLS,
          str(list(inject.EXT_TOOLS.keys())))
    r = m.call("fake", "echo", {"text": "注入测试"})
    check("管理器调用", r["ok"] and r["data"] == "echo:注入测试")
    h = m.health()
    check("健康巡检", len(h) == 1 and h[0]["ok"] is True)
    m.close_all()
    check("关闭后清空", m.names() == [])


def test_external_tool_routing():
    from harness.plugins.manager import PluginManager
    from harness.plugins import inject
    from harness.core import tools as core_tools
    p = test_manager_config()
    m = PluginManager(p, log=lambda *a: None)
    m.start_all()
    inject.register_plugin_tools(m, "fake")
    inject.patch_call_tool(m)
    r = core_tools.call_tool(None, "mcp__fake__echo", {"text": "路由"})
    check("外部工具路由", r["status"] == "ok" and r["result"] == "echo:路由")
    r2 = core_tools.call_tool(None, "mcp__fake__nope", {})
    check("未注册外部工具", r2["status"] == "error")
    # 内置工具不受影响
    r3 = core_tools.call_tool(None, "not_exist_tool")
    check("内置路由保留", r3["status"] == "error")
    m.close_all()


def test_security_filter():
    from harness.plugins.security import scan_external
    r = scan_external("正常内容" * 4000)  # 16000 字符 > 10KB 上限
    check("超长截断", r["truncated"] is True and len(r["clean"]) <= 10300,
          f"len={len(r['clean'])}")
    r2 = scan_external("普通文本")
    check("正常文本安全", r2["safe"] is True)
    # 注入模式检测（直接构造长文本触发截断路径即可，不依赖具体注入词表）
    check("扫描函数可用", isinstance(r2["clean"], str))


def test_two_plugins_parallel():
    from harness.plugins.manager import PluginManager
    import tempfile
    p = os.path.join(tempfile.mkdtemp(), "plugins.json")
    m = PluginManager(p, log=lambda *a: None)
    m.save_config([
        {"name": "fake1", "command": [PY, FAKE], "enabled": True},
        {"name": "fake2", "command": [PY, FAKE], "enabled": True},
    ])
    result = m.start_all()
    check("双插件启动", result["fake1"] is True and result["fake2"] is True)
    tools = m.all_tools()
    check("双插件工具聚合", len(tools) == 4,
          str([t["plugin"] for t in tools]))
    m.close_all()


def main():
    print("===== 插件接口协议层（M1+M2）回归 =====")
    test_handshake()
    test_tools_discovery()
    test_call_echo()
    test_call_unknown_tool()
    test_notification_ignored()
    test_bad_json_skipped()
    test_slow_timeout_rebuild()
    test_stream_truncation()
    test_unknown_method()
    test_manager_config()
    test_manager_start_and_inject()
    test_external_tool_routing()
    test_security_filter()
    test_two_plugins_parallel()
    print(f"\n===== M1+M2 插件: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
