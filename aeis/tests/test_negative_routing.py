# -*- coding: utf-8 -*-
"""test_negative_routing · C1 负路由单元测试（智能论 v3.4 6章.2）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from negative_routing import NegativeRouting, CAPABILITY_NA_EXAMPLES

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

nr = NegativeRouting()

# C1-1: 邻域混淆——任务条件含不适用条件 → 拒绝
cands = [
    {"id": "BFS", "score": 0.9, "not_applicable": ["最短路径", "加权图"]},
    {"id": "DFS", "score": 0.7, "not_applicable": ["分层遍历"]},
]
r1 = nr.negative_filter(cands, task_conditions={"广度优先", "最短路径"})
check("BFS rejected on shortest path", len(r1["rejected"]) == 1 and r1["rejected"][0]["id"] == "BFS", str(r1["rejected"]))

# C1-2: 无冲突 → 全部幸存
r2 = nr.negative_filter(cands, task_conditions={"图遍历"})
check("all survive when no NA hit", len(r2["survivors"]) == 2 and len(r2["rejected"]) == 0)

# C1-3: 无任务条件 → 不拒绝（保守：无信息不拒绝）
r3 = nr.negative_filter(cands, task_conditions=set())
check("no task conditions no reject", len(r3["rejected"]) == 0)

# C1-4: 拒绝率统计
check("rejection rate tracked", r1["rejection_rate"] > 0)

# C1-5: 能力级示例可用
check("capability examples exist", "广度优先搜索" in CAPABILITY_NA_EXAMPLES)

# C1-6: 模拟 dsh-memory 实证趋势（28%→88%→91%）
# 无能力级不适用条件时：邻域任务几乎全误接受（低拒绝率）
nr2 = NegativeRouting()
naive_cands = [{"id": f"c{i}", "score": 0.8, "not_applicable": []} for i in range(10)]
r_naive = nr2.negative_filter(naive_cands, task_conditions={"最短路径"})
check("naive low rejection", r_naive["rejection_rate"] == 0.0)

# 有能力级不适用条件时：邻域任务被拒绝
nr3 = NegativeRouting()
na_cands = [{"id": f"c{i}", "score": 0.8, "not_applicable": ["最短路径"] if i % 2 == 0 else []} for i in range(10)]
r_na = nr3.negative_filter(na_cands, task_conditions={"最短路径"})
check("with NA higher rejection", r_na["rejection_rate"] > r_naive["rejection_rate"], str(r_na["rejection_rate"]))

print(f"\nC1 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
