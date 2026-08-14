#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编码能力（harness.coding）回归测试
==================================
覆盖四项能力：
- 能修改：workspace 读写/文件操作
- 能恢复：写前自动快照 + 回滚
- 能验证：run_command 执行测试命令
- 能记录：任务步骤留痕/管理器状态
- 护栏：路径越界拒绝/禁 shell 命令
check 框架。
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


def make_ws():
    root = tempfile.mkdtemp()
    return root


def test_workspace_modify():
    """能修改：read/write/list/exists。"""
    from harness.coding.workspace import Workspace
    root = make_ws()
    ws = Workspace(root)
    r = ws.write_file("hello.py", "def hello():\n    return 42\n")
    check("写入文件", r["ok"] and r["chars"] > 0)
    r2 = ws.read_file("hello.py")
    check("读取文件", r2["ok"] and "return 42" in r2["content"])
    r3 = ws.list_files(".")
    check("列出目录", r3["ok"] and len(r3["items"]) == 1)
    r4 = ws.exists("hello.py")
    check("存在检查", r4["exists"] is True)
    # 越界拒绝
    r5 = ws.write_file("../evil.py", "x")
    check("越界拒绝", r5["ok"] is False)
    r6 = ws.read_file("../etc/passwd")
    check("越界读取拒绝", r6["ok"] is False)


def test_workspace_revert():
    """能恢复：写前快照 + 回滚。"""
    from harness.coding.workspace import Workspace
    root = make_ws()
    ws = Workspace(root)
    ws.write_file("a.py", "v1\n")
    # 第二次写（覆盖）→ 自动快照 v1
    ws.write_file("a.py", "v2\n")
    snaps = ws.list_snapshots()
    check("写前自动快照", len(snaps) >= 1, f"{len(snaps)} 个快照")
    r = ws.read_file("a.py")
    check("内容已改 v2", "v2" in r["content"])
    # 回滚
    rr = ws.revert(snaps[0]["id"])
    check("回滚成功", rr["ok"] and rr["restored"] >= 1)
    r2 = ws.read_file("a.py")
    check("内容恢复 v1", "v1" in r2["content"], r2["content"])


def test_command_verify():
    """能验证：run_command 执行测试（禁 shell）。"""
    from harness.coding.workspace import Workspace
    root = make_ws()
    ws = Workspace(root)
    ws.write_file("t.py", "print('OK42')\n")
    # 字符串命令拒绝
    loop = None
    from harness.coding.loop import CodingLoop
    loop = CodingLoop(ws, env={}, log=lambda *a: None)
    r = loop._execute_tool("run_command", {"command": "python t.py"})
    check("禁 shell 字符串", r["ok"] is False)
    # 参数列表执行
    r2 = loop._execute_tool("run_command", {"command": [sys.executable, "t.py"]})
    check("参数列表执行", r2["ok"] is True and "OK42" in str(r2.get("result", "")))


def test_manager_record():
    """能记录：任务提交/状态/快照列表（不真实跑 LLM，验证管理面）。"""
    from harness.coding.manager import CodingManager
    root = make_ws()
    # 用假 env（无 key）提交会失败但不崩——验证管理面
    mgr = CodingManager(env={"DEEPSEEK_API_KEY": ""}, log=lambda *a: None)
    mgr.set_default_workspace(root)
    r = mgr.submit("测试任务（无 key 将失败）")
    check("任务提交", r["ok"] and r["task_id"].startswith("code_"))
    time.sleep(1.5)
    entry = mgr.get(r["task_id"])
    check("任务状态记录", entry is not None and entry["status"] in
          ("running", "error", "succeeded"))
    lst = mgr.list_tasks()
    check("任务历史", len(lst) >= 1 and lst[0]["task_id"] == r["task_id"])
    # 回滚管理面
    rr = mgr.revert(r["task_id"])
    check("管理器回滚接口", isinstance(rr, dict) and ("ok" in rr or "error" in rr))


def test_loop_tools():
    """loop 工具执行面（read/write/list/revert）。"""
    from harness.coding.loop import CodingLoop
    from harness.coding.workspace import Workspace
    root = make_ws()
    ws = Workspace(root)
    loop = CodingLoop(ws, env={}, log=lambda *a: None)
    r = loop._execute_tool("write_file", {"path": "x.py", "content": "1"})
    check("工具写入", r["ok"] is True)
    r2 = loop._execute_tool("read_file", {"path": "x.py"})
    check("工具读取", r2["ok"] and r2["result"] == "1")
    r3 = loop._execute_tool("list_files", {"dir": "."})
    check("工具列出", r3["ok"] and "x.py" in str(r3["result"]))
    r4 = loop._execute_tool("revert", {})
    check("工具回滚", r4["ok"] is True)
    r5 = loop._execute_tool("unknown_tool", {})
    check("未知工具", r5["ok"] is False)


def main():
    print("===== 编码能力（能修改/能恢复/能验证/能记录）回归 =====")
    test_workspace_modify()
    test_workspace_revert()
    test_command_verify()
    test_manager_record()
    test_loop_tools()
    print(f"\n===== 编码能力: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
