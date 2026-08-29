# -*- coding: utf-8 -*-
"""test_curiosity_mcp · 里程碑3.3 curiosity_explorer MCP 集成测试"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.core import SpacetimeMemoryEngine as AEISEngine

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

d = tempfile.mkdtemp()
eng = AEISEngine(db_path=os.path.join(d, "t.db"))

# create 物理世界
r1 = eng.curiosity_explorer("create", {"size": 24, "trees": 2})
check("create ok", r1["status"] == "ok" and r1["scene"]["status"] == "ok", str(r1))

# entity 追逐链
r2 = eng.curiosity_explorer("entity", {"category": "player", "behavior": "wander", "pos": [2, 1.5, 2], "speed": 0.5})
check("player added", r2["status"] == "ok" and "entity_id" in r2, str(r2))
pid = r2["entity_id"]
r3 = eng.curiosity_explorer("entity", {"category": "wolf", "behavior": "seek", "pos": [15, 1.5, 15], "speed": 0.6, "goal": pid})
check("wolf added", r3["status"] == "ok", str(r3))
r4 = eng.curiosity_explorer("entity", {"category": "rabbit", "behavior": "flee", "pos": [10, 1.5, 10], "speed": 0.5, "goal": r3["entity_id"]})
check("rabbit added", r4["status"] == "ok", str(r4))

# 预热（全带宽）→ 探索
eng.curiosity_explorer("explore", {"n": 6, "budget": 3})
r5 = eng.curiosity_explorer("explore", {"n": 30, "budget": 2, "policy": "curiosity"})
check("explore ok", r5["status"] == "ok" and r5["explore"]["status"] == "ok"
      and len(r5["explore"]["obs_distribution"]) == 3, str(r5))

# probe 全带宽探针
r6 = eng.curiosity_explorer("probe", {"n": 10})
check("probe ok", r6["status"] == "ok" and "learned_rate" in r6["probe"], str(r6))

# compare 策略对比
r7 = eng.curiosity_explorer("compare", {"budget": 2, "explore_ticks": 30, "probe_ticks": 10})
rc = r7["compare"]["results"]
check("compare ok", r7["status"] == "ok" and set(rc.keys())
      == {"curiosity", "random", "round_robin"}, str(r7))
check("compare curiosity wins probe",
      rc["curiosity"]["probe_rate"] > rc["random"]["probe_rate"], str(rc["curiosity"]["probe_rate"]))

# curiosity 好奇心摘要
r8 = eng.curiosity_explorer("curiosity", {})
check("curiosity summary", r8["status"] == "ok" and "observations" in r8["curiosity"]
      and "uncertainty_trend" in r8["curiosity"], str(r8))

# uncertainty 轨迹
r9 = eng.curiosity_explorer("uncertainty", {})
check("uncertainty curve", r9["status"] == "ok" and len(r9["curve"]) > 0
      and r9["current"] > 0.0, str(r9))

# step 决策日志
r10 = eng.curiosity_explorer("step", {"budget": 2, "policy": "curiosity"})
check("step log", r10["status"] == "ok" and len(r10["step"]["chosen"]) == 2
      and "ig_scores" in r10["step"], str(r10))

# model + state
r11 = eng.curiosity_explorer("model", {})
check("model export", r11["status"] == "ok" and "per_entity" in r11["model"], str(r11))
r12 = eng.curiosity_explorer("state", {})
check("state ok", r12["status"] == "ok" and r12["explorer"]["status"] == "ok", str(r12))

# unknown action
r13 = eng.curiosity_explorer("bogus", {})
check("unknown action error", r13["status"] == "error", str(r13))

print(f"\nCURIOSITY-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
