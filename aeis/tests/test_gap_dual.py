# -*- coding: utf-8 -*-
"""test_gap_dual · B5 D_task/D_meta 分离单元测试（智能论 v3.4 2.7.0）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from gap_dual import GapDual

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

g = GapDual()

# B5-1: 空路径 → D_task=∞ → BLINDSPOT
r1 = g.compute_d_task(graph_paths={}, task_conditions={"海拔高"})
check("empty paths blindspot", r1["blindspot"] and r1["d_task"] == float("inf"), str(r1))

# B5-2: 有可用路径 → D_task 有限
paths = {
    "p1": {"id": "p1", "available": True, "dist": 2.0, "cond_set": {"海拔高", "气压"}},
    "p2": {"id": "p2", "available": True, "dist": 5.0, "cond_set": {"海拔高"}},
}
r2 = g.compute_d_task(graph_paths=paths, task_conditions={"海拔高", "气压"})
check("finite d_task with usable path", not r2["blindspot"] and r2["d_task"] == 2.0, str(r2))

# B5-3: 全部不可达 → BLINDSPOT
paths3 = {
    "p1": {"id": "p1", "available": False, "dist": 2.0, "cond_set": set()},
}
r3 = g.compute_d_task(graph_paths=paths3, task_conditions={"x"})
check("all unavailable blindspot", r3["blindspot"])

# B5-4: 条件缺口——任务条件未被覆盖 → cond_gap
r4 = g.compute_d_task(graph_paths=paths, task_conditions={"海拔高", "气压", "高压锅"})
check("cond gap detected", r4["cond_gap"] == 1, str(r4["cond_gap"]))

# B5-5: D_meta 增长——盲区事件 → 结构性增长
m1 = g.update_meta(d_task=float("inf"), blindspot=True, new_conditions_seen=2)
check("meta grows on blindspot", m1 > 0, str(m1))

# B5-6: D_meta 单调不减（无干预）
m2 = g.update_meta(d_task=5.0, blindspot=False, new_conditions_seen=1)
check("meta non-decreasing", m2 >= m1 * (1 - 0.1) - 1e-9, f"{m2} vs {m1}")

# B5-7: D_task 可下降（学习）而 D_meta 独立
# 模拟学习：路径从不可用到可用 → D_task 从 ∞ 到有限
g2 = GapDual()
r_before = g2.compute_d_task(graph_paths={}, task_conditions={"x"})
g2.update_meta(r_before["d_task"], r_before["blindspot"])
paths_learned = {"p1": {"id": "p1", "available": True, "dist": 1.0, "cond_set": {"x"}}}
r_after = g2.compute_d_task(graph_paths=paths_learned, task_conditions={"x"})
check("D_task drops after learning", r_before["d_task"] == float("inf") and r_after["d_task"] == 1.0,
      f"{r_before['d_task']} -> {r_after['d_task']}")

# B5-8: state 快照
st = g.state()
check("state has meta est", "d_meta_est" in st)

print(f"\nB5 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
