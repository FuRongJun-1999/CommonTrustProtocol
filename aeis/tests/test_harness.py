#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
原生运行时（Native Harness）回归测试
====================================
覆盖：config 加载 / cron 解析 / store 建库与种子 / 调度引擎到期执行 /
心跳任务 / 睡眠任务 / 工具注册表 / 会话上下文。check 框架（直接运行）。
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


def test_config():
    from harness.core.config import load_config, DEFAULT_CONFIG_PATH
    cfg = load_config()
    check("config 默认身份", cfg["env"]["AEIS_IDENTITY"] == "灵枢",
          cfg["env"]["AEIS_IDENTITY"])
    check("config 模型默认", cfg["model"]["name"] == "deepseek-chat")
    check("config 密钥存在", "DEEPSEEK_API_KEY" in cfg["env"])
    # 自定义文件
    p = os.path.join(tempfile.mkdtemp(), "cfg.json")
    with open(p, "w", encoding="utf-8") as f:
        f.write('{"model": {"name": "test-model"}, "voice": {"enabled": false}}')
    cfg2 = load_config(p)
    check("config 文件覆盖", cfg2["model"]["name"] == "test-model")
    check("config 部分合并", cfg2["voice"]["enabled"] is False)


def test_cron():
    from harness.scheduler.cron import next_run
    now = time.time()
    r = next_run(now, {"type": "interval", "minutes": 30}, None)
    check("cron interval 30m", 29 * 60 < r - now < 31 * 60, f"+{(r-now)/60:.1f}m")
    r2 = next_run(now, {"type": "interval", "minutes": 5}, now)
    check("cron interval 锚点", abs((r2 - now) - 300) < 5)
    r3 = next_run(now, {"type": "daily", "hour": 1, "minute": 0}, None)
    import datetime
    dt = datetime.datetime.fromtimestamp(r3)
    check("cron daily 01:00", dt.hour == 1 and dt.minute == 0,
          f"{dt.strftime('%H:%M')}")
    r4 = next_run(now, {"type": "cron", "expr": "*/15 * * * *"}, None)
    check("cron 表达式 */15", 0 < r4 - now <= 15 * 60, f"+{(r4-now)/60:.1f}m")
    r5 = next_run(now, {"type": "bad-type"}, None)
    check("cron 未知类型兜底", r5 - now == 1800)


def test_store():
    from harness.scheduler.store import AutomationStore
    db = os.path.join(tempfile.mkdtemp(), "auto.db")
    s = AutomationStore(db)
    s.add("t1", "测试任务", {"type": "interval", "minutes": 1}, "heartbeat",
          next_run_at=time.time() - 1)  # 已到期
    s.add("t2", "未来任务", {"type": "interval", "minutes": 30}, "sleep",
          next_run_at=time.time() + 3600)
    due = s.list_due()
    check("store 到期查询", [a["id"] for a in due] == ["t1"],
          str([a["id"] for a in due]))
    run_id = s.mark_run("t1", time.time() + 60, "succeeded", detail="ok")
    check("store run 记录", s.get("t1")["run_count"] == 1)
    runs = s.recent_runs()
    check("store recent_runs", len(runs) >= 1 and runs[0]["run_id"] == run_id)
    s.set_enabled("t2", 0)
    check("store 禁用", s.list_due() == [])
    s.close()


def test_engine(tmp_agent=None):
    from harness.scheduler.store import AutomationStore
    from harness.scheduler.engine import SchedulerEngine
    db = os.path.join(tempfile.mkdtemp(), "auto2.db")
    s = AutomationStore(db)
    calls = []

    def fake_task(agent, ctx):
        calls.append(ctx["automation"]["id"])
        return "fake ok"

    eng = SchedulerEngine(s, None, tick_seconds=1, log=lambda *a: None)
    eng.register("fake", fake_task)
    s.add("f1", "立即任务", {"type": "interval", "minutes": 1}, "fake",
          next_run_at=time.time() - 0.5)
    eng.start()
    time.sleep(2.5)
    eng.stop()
    check("engine 到期执行", "f1" in calls, str(calls))
    auto = s.get("f1")
    check("engine run_count", auto["run_count"] >= 1)
    check("engine next 推进", auto["next_run_at"] > time.time() - 1)
    runs = s.recent_runs()
    check("engine run 成功", runs and runs[0]["outcome"] == "succeeded")
    s.close()


def test_tools_registry():
    from harness.core.tools import TOOL_REGISTRY, call_tool
    check("tools 注册表规模", len(TOOL_REGISTRY) >= 30, f"{len(TOOL_REGISTRY)} 工具")
    check("tools 关键工具", all(k in TOOL_REGISTRY for k in
                                ("remember", "recall", "cognition_cycle", "device_call")))
    r = call_tool(None, "not_exist_tool")
    check("tools 未知工具容器化", r["status"] == "error")


def test_session():
    from harness.core.session import Session
    s = Session(agent=None, persist=False)
    s.add("user", "你好")
    s.add("assistant", "你好呀")
    check("session 历史", len(s.history) == 2)
    check("session 上限", (Session(agent=None, max_history=3, persist=False) and True))
    s2 = Session(agent=None, max_history=3, persist=False)
    for i in range(6):
        s2.add("user", f"m{i}")
    check("session 截断", len(s2.history) == 3 and s2.history[-1]["content"] == "m5")


def test_main_import():
    import harness.main
    check("main 可导入", hasattr(harness.main, "main") and hasattr(harness.main, "seed_default_automations"))


def main():
    print("===== 原生运行时（Native Harness）回归 =====")
    test_config()
    test_cron()
    test_store()
    test_engine()
    test_tools_registry()
    test_session()
    test_main_import()
    print(f"\n===== harness 回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
