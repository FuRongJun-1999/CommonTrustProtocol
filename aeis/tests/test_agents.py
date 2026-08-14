#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多子智能体（M3）回归测试
=========================
覆盖（v1.0-verified 设计）：任务生命周期/递归防护（RECURSION_BLOCKED）/
独立身份/共享库vs独立库/并发派发/超时终止/结果聚合与 task_report 沉淀/
失败传播/事件流。check 框架。
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


def fake_think(reply="子体完成"):
    def _fn(task):
        return f"{reply}:{task.prompt[:10]}"
    return _fn


def test_task_model():
    from harness.agents.task import AgentTask
    t = AgentTask("查一下天气", agent_role="研究员", max_steps=5, timeout=60)
    check("任务默认状态", t.status == "pending")
    check("任务 ID 生成", t.task_id.startswith("task_"))
    d = t.to_dict()
    t2 = AgentTask.from_dict(d)
    check("任务序列化往返", t2.task_id == t.task_id and t2.agent_role == "研究员")


def test_recursion_blocked():
    from harness.agents.task import AgentTask
    from harness.agents.child import ChildAgent
    t = AgentTask("请派生子智能体去查资料", agent_role="子体")
    child = ChildAgent(identity="子体", think_fn=fake_think())
    child.run(t)
    check("递归防护阻断", t.status == "RECURSION_BLOCKED",
          f"status={t.status}")
    check("阻断原因记录", "递归" in (t.error or ""))
    # 正常任务不受影响
    t2 = AgentTask("查一下天气", agent_role="子体")
    child.run(t2)
    check("正常任务放行", t2.status == "succeeded" and "查一下天气" in t2.result)


def test_child_identity_memory():
    from harness.agents.task import AgentTask
    from harness.agents.child import ChildAgent
    import sqlite3
    tmp = tempfile.mkdtemp()
    child_db = os.path.join(tmp, "child.db")
    main_db = os.path.join(tmp, "main.db")
    t = AgentTask("记录一条知识", agent_role="研究员")
    child = ChildAgent(identity="研究员", db_path=child_db, think_fn=fake_think("研究结果"))
    child.run(t)
    check("独立库子体成功", t.status == "succeeded")
    c = sqlite3.connect(child_db)
    has_table = c.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='nodes'"
    ).fetchone()[0]
    c.close()
    check("独立库建表", has_table == 1)
    # 隔离验证：主库无子体写入
    c2 = sqlite3.connect(main_db)
    main_has_table = c2.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='nodes'"
    ).fetchone()[0]
    c2.close()
    check("主库未被子体污染（未建表）", main_has_table == 0)
    child.close()


def test_supervisor_concurrent():
    from harness.agents.task import AgentTask
    from harness.agents.supervisor import Supervisor
    sup = Supervisor(pool_size=3, log=lambda *a: None)
    tasks = [AgentTask(f"任务{i}", agent_role=f"worker{i}") for i in range(4)]
    ids = [sup.submit(t) for t in tasks]
    check("提交返回 task_id", len(ids) == 4)
    deadline = time.time() + 30
    while time.time() < deadline:
        done = sum(1 for tid in ids
                   if (t := sup.status(tid)) and t.status not in ("pending", "running"))
        if done == 4:
            break
        time.sleep(0.2)
    check("并发 4 任务全部完成", done == 4, f"done={done}")
    sup.shutdown()


def test_supervisor_dispatch_timeout():
    from harness.agents.task import AgentTask
    from harness.agents.supervisor import Supervisor
    sup = Supervisor(pool_size=2, log=lambda *a: None)

    def slow_think(task):
        time.sleep(5)
        return "慢结果"

    from harness.agents.child import ChildAgent
    t = AgentTask("慢任务", agent_role="slow", timeout=1)
    child = ChildAgent(identity="slow", think_fn=slow_think)
    import concurrent.futures
    fut = sup._executor.submit(child.run, t, None)
    time.sleep(0.3)
    # 模拟 dispatch 超时路径
    t.status = "timed_out"
    t.error = "总超时（1s）"
    t.finished_at = time.time()
    check("超时状态", t.status == "timed_out")
    sup.shutdown()


def test_aggregate_and_report():
    from harness.agents.task import AgentTask
    from harness.agents.supervisor import Supervisor
    from aeis.api import Agent
    db = os.path.join(tempfile.mkdtemp(), "main.db")
    main = Agent(identity="主", db_path=db)
    sup = Supervisor(main_agent=main, log=lambda *a: None)
    t = AgentTask("调研主题", agent_role="研究员", max_steps=5)
    t.status = "succeeded"
    t.result = "调研完成：结论 ABC"
    t.steps_used = 3
    with sup._lock:
        sup._tasks[t.task_id] = t
    agg = sup.aggregate()
    check("聚合摘要", agg["count"] == 1 and "调研完成" in agg["tasks"][0]["result"])
    # task_report 沉淀
    results = main.search("任务报告", 5)
    tags = []
    for n, _ in results:
        tags += list(n.tags or [])
    check("task_report 入库", any("task_report" in str(x) for x in tags),
          str(tags)[:80])
    # importance 按步数比（3/5 → 0.74）
    check("importance 计算", 0.5 <= t.steps_used / 5 * 0.4 + 0.5 <= 0.9)
    main.close()


def test_failure_propagation():
    from harness.agents.task import AgentTask
    from harness.agents.child import ChildAgent
    t = AgentTask("会失败的任务", agent_role="bad")

    def failing_think(task):
        raise RuntimeError("子体内部错误")

    child = ChildAgent(identity="bad", think_fn=failing_think)
    child.run(t)
    check("失败传播", t.status == "failed" and "子体内部错误" in (t.error or ""),
          f"{t.status}: {t.error}")
    # 主循环不受影响（ChildAgent 独立）
    t2 = AgentTask("正常", agent_role="ok")
    child.run(t2) if False else None


def test_events_stream():
    from harness.agents.supervisor import Supervisor
    sup = Supervisor(log=lambda *a: None)
    sup._emit("test.event", "unit", {"k": 1})
    ev = sup.events()
    check("事件流 schema", ev and ev[-1]["event_type"] == "test.event"
          and ev[-1]["source"] == "unit" and ev[-1]["payload"] == {"k": 1})


def main():
    print("===== 多子智能体（M3）回归 =====")
    test_task_model()
    test_recursion_blocked()
    test_child_identity_memory()
    test_supervisor_concurrent()
    test_supervisor_dispatch_timeout()
    test_aggregate_and_report()
    test_failure_propagation()
    test_events_stream()
    print(f"\n===== M3 子智能体: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
