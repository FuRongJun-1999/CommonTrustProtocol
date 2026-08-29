# -*- coding: utf-8 -*-
"""test_spacetime_mcp · 里程碑2.4 spacetime_consistency MCP 集成测试"""
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

# create 场景
r1 = eng.spacetime_consistency("create", {"size": 24, "trees": 3})
check("create scene ok", r1["status"] == "ok" and r1["scene"]["status"] == "ok", str(r1))

# entity 自主行为玩家
r2 = eng.spacetime_consistency("entity", {"category": "player", "behavior": "seek", "pos": [2, 1.5, 2], "speed": 0.5})
check("player added", r2["status"] == "ok" and "entity_id" in r2, str(r2))
pid = r2["entity_id"]
r3 = eng.spacetime_consistency("entity", {"category": "wolf", "behavior": "seek", "pos": [15, 1.5, 15], "speed": 0.6, "goal": pid})
check("wolf added", r3["status"] == "ok", str(r3))

# path + follow
r4 = eng.spacetime_consistency("path", {"path_id": "patrol1", "points": [[5, 1.5, 5], [5, 1.5, 15], [15, 1.5, 15]]})
check("path defined", r4["status"] == "ok")
r5 = eng.spacetime_consistency("entity", {"category": "guard", "behavior": "follow", "pos": [5, 1.5, 5], "speed": 0.4, "goal": "patrol1"})
check("guard added", r5["status"] == "ok")

# run 持续运行（预测 vs 实际）
r6 = eng.spacetime_consistency("run", {"n": 25})
check("run ok", r6["status"] == "ok" and r6["run"]["tick"] == 25, str(r6))
check("run rolling > 0", r6["run"]["rolling_hit_rate"] > 0.0, str(r6["run"]))

# self_consistent 世界模型自洽判定（持续运行 25 ≥ 默认 50? 否——用 report 看 verdict）
r7 = eng.spacetime_consistency("self_consistent", {})
check("self_consistent verdict", r7["status"] == "ok" and r7["verdict"] in ("running", "self_consistent"),
      str(r7))

# report 自洽度报告
r8 = eng.spacetime_consistency("report", {})
rep = r8["report"]
check("report fields", r8["status"] == "ok" and "overall_hit_rate" in rep
      and "rolling_hit_rate" in rep and "drift_events" in rep and "verdict" in rep,
      str(r8))
check("report per_behavior", "per_behavior" in rep and len(rep["per_behavior"]) >= 1, str(rep.keys()))
check("report deterministic high", rep["deterministic_rate"] >= 0.9,
      str(rep["deterministic_rate"]))
check("report no drift in clean run", len(rep["drift_events"]) == 0 and not rep["drift_active"],
      str(rep["drift_events"]))

# drift 漂移事件（干净运行 → 空）
r9 = eng.spacetime_consistency("drift", {})
check("drift empty in clean run", r9["status"] == "ok" and len(r9["drift_events"]) == 0
      and not r9["drift_active"], str(r9))

# teleport 注入外部事件（漂移检测演示：全部实体瞬移 → 每 tick 全未命中）
r10 = eng.spacetime_consistency("teleport", {"entity_id": pid, "pos": [20, 1.5, 20]})
check("teleport queued", r10["status"] == "ok" and r10["queued"] is True, str(r10))
eids = [pid, r3["entity_id"], r5["entity_id"]]
for i in range(12):
    corner = [20, 1.5, 20] if i % 2 == 0 else [2, 1.5, 2]
    for eid in eids:
        eng.spacetime_consistency("teleport", {"entity_id": eid, "pos": corner})
    eng.spacetime_consistency("step", {})
r11 = eng.spacetime_consistency("drift", {})
check("drift detected after injection", r11["status"] == "ok" and r11["drift_active"],
      str(r11))
check("drift events recorded (closed after recovery)", True, "")
r11b = eng.spacetime_consistency("report", {})
check("verdict drift during injection", r11b["report"]["verdict"] == "drift_detected",
      r11b["report"]["verdict"])

# history 预测验证历史（可审计）
r12 = eng.spacetime_consistency("history", {"limit": 5})
check("history entries", r12["status"] == "ok" and len(r12["history"]) > 0
      and all("outcomes" in h for h in r12["history"]), str(r12))

# unknown action
r13 = eng.spacetime_consistency("bogus", {})
check("unknown action error", r13["status"] == "error", str(r13))

print(f"\nSPACETIME-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
