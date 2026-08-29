# -*- coding: utf-8 -*-
"""test_seven_layer_mcp · 里程碑3.4 seven_layer_loop MCP 集成测试"""
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

# create + entities
r1 = eng.seven_layer_loop("create", {"size": 24, "trees": 2})
check("create ok", r1["status"] == "ok" and r1["scene"]["status"] == "ok", str(r1))
r2 = eng.seven_layer_loop("entity", {"category": "player", "behavior": "wander", "pos": [2, 1.5, 2], "speed": 0.5})
check("player added", r2["status"] == "ok" and "entity_id" in r2, str(r2))
pid = r2["entity_id"]
r3 = eng.seven_layer_loop("entity", {"category": "wolf", "behavior": "seek", "pos": [15, 1.5, 15], "speed": 0.6, "goal": pid})
check("wolf added", r3["status"] == "ok", str(r3))
r4 = eng.seven_layer_loop("entity", {"category": "rabbit", "behavior": "flee", "pos": [10, 1.5, 10], "speed": 0.5, "goal": r3["entity_id"]})
check("rabbit added", r4["status"] == "ok", str(r4))

# run 闭环
r5 = eng.seven_layer_loop("run", {"n": 60})
check("run ok", r5["status"] == "ok" and r5["run"]["loop_tick"] == 60
      and r5["run"]["overall_hit_rate"] > 0.0, str(r5))

# step 单步七层留痕
r6 = eng.seven_layer_loop("step", {})
st = r6["step"]
check("step seven layers", r6["status"] == "ok" and all(k in st for k in
      ("L1_perception", "L2_memory", "L3_cognition", "L4_prediction",
       "L5_verification", "L6_physics", "L7_decision")), str(st.keys()))

# report 闭环报告
r7 = eng.seven_layer_loop("report", {})
rep = r7["report"]
check("report ok", r7["status"] == "ok" and "L5_verification" in rep
      and "closed_loop_enhancement" in rep and rep["loop_closed"] is True, str(r7))
check("report hit rate", 0.0 < rep["L5_verification"]["overall_hit_rate"] <= 1.0,
      str(rep["L5_verification"]["overall_hit_rate"]))
check("report enhancement", rep["closed_loop_enhancement"]["improvement"] >= 0.0,
      str(rep["closed_loop_enhancement"]))

# audit 审计轨迹
r8 = eng.seven_layer_loop("audit", {"limit": 5})
check("audit ok", r8["status"] == "ok" and len(r8["audit"]) == 5
      and "L1_perception" in r8["audit"][-1], str(r8))

# verify / decision / memory / graph
r9 = eng.seven_layer_loop("verify", {})
check("verify ok", r9["status"] == "ok" and "hit_rate" in r9["verify"], str(r9))
r10 = eng.seven_layer_loop("decision", {})
check("decision ok", r10["status"] == "ok" and "obs_distribution" in r10["decision"],
      str(r10))
r11 = eng.seven_layer_loop("memory", {})
check("memory ok", r11["status"] == "ok" and "history_len" in r11["memory"], str(r11))
r12 = eng.seven_layer_loop("graph", {})
check("graph ok", r12["status"] == "ok" and "relations" in r12["graph"], str(r12))
r13 = eng.seven_layer_loop("state", {})
check("state ok", r13["status"] == "ok" and r13["loop"]["status"] == "ok", str(r13))

# unknown
r14 = eng.seven_layer_loop("bogus", {})
check("unknown action error", r14["status"] == "error", str(r14))

print(f"\nSEVENLAYER-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
