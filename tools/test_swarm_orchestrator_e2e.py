# -*- coding: utf-8 -*-
"""test_swarm_orchestrator_e2e.py · 编排层批 3 端到端 demo（V-SO.6/7，2026-08-29）

复合任务「统计→排序→校验」三步 DAG 跨节点协作：
- V-SO.6 否决式融合：任一子任务 fail → 整体 fail + 下游跳过
- V-SO.7 端到端：全 pass + 消息/结果可追溯
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_orchestrator import (Registry, RoleNegotiator, TaskGraph,
                                Dispatcher, Orchestrator)
from swarm_m3_trust import TrustLedger

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="so_e2e_")
try:
    trust = TrustLedger()
    trust.record("nodeB", True); trust.record("nodeB", True)
    reg = Registry(os.path.join(tmp, "bus"))
    reg.register("nodeA", ["校验", "编排"])
    reg.register("nodeB", ["求和", "世界模型"])
    reg.register("nodeC", ["求和", "排序"])

    # 端到端 DAG：统计 → 排序 → 校验
    graph = TaskGraph([
        {"id": "stat", "capability": "求和", "input": [5, 10, 20], "depends_on": []},
        {"id": "sort", "capability": "排序", "input": [3, 1, 2], "depends_on": ["stat"]},
        {"id": "check", "capability": "校验", "input": None, "depends_on": ["sort"]},
    ])
    executors = {
        "求和": lambda xs: sum(xs),
        "排序": lambda xs: sorted(xs),
        "校验": lambda _: "schema ok",
    }

    # ============ V-SO.7 端到端（全 pass） ============
    orch = Orchestrator(graph, Dispatcher(reg, trust), executors)
    r = orch.run()
    check("V-SO.7 全 pass", r["passed"] and r["summary"] == "3/3 子任务通过",
          r["summary"])
    check("V-SO.7 结果可追溯", r["results"]["stat"]["output"] == 35
          and r["results"]["sort"]["output"] == [1, 2, 3]
          and r["results"]["check"]["output"] == "schema ok",
          str(r["results"])[:120])

    # ============ V-SO.6 否决式融合 ============
    executors_bad = dict(executors)
    executors_bad["排序"] = lambda xs: (_ for _ in ()).throw(ValueError("模拟执行失败"))
    orch2 = Orchestrator(graph, Dispatcher(reg, trust), executors_bad)
    r2 = orch2.run()
    check("V-SO.6 fail 子任务标记", not r2["results"]["sort"]["ok"], str(r2["results"]["sort"]))
    check("V-SO.6 下游跳过", "跳过" in str(r2["results"]["check"].get("error", "")),
          str(r2["results"]["check"]))
    check("V-SO.6 整体否决", not r2["passed"], r2["summary"])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"编排层批 3 端到端: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
