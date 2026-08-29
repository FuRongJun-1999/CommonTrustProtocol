# -*- coding: utf-8 -*-
"""test_seven_layer_loop · 里程碑3.4 七层闭环单元测试（阶段3收官）
（感知→记忆→理解→预测→验证→物理→决策 完整自主循环 + 审计轨迹）"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.seven_layer_loop import SevenLayerLoop

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

def make_loop(budget=2):
    loop = SevenLayerLoop(size=24, budget=budget)
    loop.create_scene(trees=2, water=False)
    p = loop.add_entity("player", behavior="wander", pos=(2, 1.5, 2), speed=0.5)
    w = loop.add_entity("wolf", behavior="seek", pos=(15, 1.5, 15), speed=0.6, goal=p)
    r = loop.add_entity("rabbit", behavior="flee", pos=(10, 1.5, 10), speed=0.5, goal=w)
    return loop, p, w, r

# ---------- 1. 闭环运行（七层持续循环） ----------
loop, p, w, r = make_loop()
loop.explorer.observe()
loop.explorer.run(n=loop.explorer.window)   # 预热（全带宽，模型成形）
res = loop.run(n=60)
check("run ok", res["status"] == "ok" and res["loop_tick"] == 60, str(res))
check("audit length", len(loop.audit) == 60, str(len(loop.audit)))

# 2. 审计轨迹：每 tick 七层留痕
rec = loop.audit[-1]
check("audit has all 7 layers",
      all(k in rec for k in ("L1_perception", "L2_memory", "L3_cognition",
                             "L4_prediction", "L5_verification", "L6_physics",
                             "L7_decision")), str(sorted(rec.keys())))
check("audit tick field", rec["tick"] == 60, str(rec.get("tick")))
check("L5 verification fields", "hit_rate" in rec["L5_verification"]
      and "hits" in rec["L5_verification"] and "total" in rec["L5_verification"],
      str(rec["L5_verification"]))
check("L7 decision fields", "chosen" in rec["L7_decision"]
      and "ig_scores" in rec["L7_decision"], str(rec["L7_decision"]))

# 3. 闭环报告（七层统计）
rep = loop.report()
check("report seven layers", all(k in rep for k in SevenLayerLoop.LAYERS), str(rep.keys()))
check("report overall hit rate", 0.0 < rep["L5_verification"]["overall_hit_rate"] <= 1.0,
      str(rep["L5_verification"]["overall_hit_rate"]))
check("report loop_closed", rep["loop_closed"] is True, str(rep))
check("report enhancement fields", "early_hit_rate" in rep["closed_loop_enhancement"]
      and "late_hit_rate" in rep["closed_loop_enhancement"]
      and "improvement" in rep["closed_loop_enhancement"], str(rep))

# 4. 闭环自增强：运行后段命中率 ≥ 前段（学习+好奇让闭环越跑越准）
enh = rep["closed_loop_enhancement"]
check("closed-loop self-enhancement", enh["improvement"] >= 0.0,
      f"early={enh['early_hit_rate']} late={enh['late_hit_rate']}")

# 5. 好奇决策在闭环中持续聚焦信息瓶颈（wolf 链中段 ≥ rabbit 下游）
od = rep["L7_decision"]["obs_distribution"]
ids = list(od.keys())
_pp, _ww, _rr = ids[0], ids[1], ids[2]
check("bottleneck focus in loop (wolf >= rabbit)", od[_ww] >= od[_rr],
      f"wolf={od[_ww]} rabbit={od[_rr]}")

# 6. 各层状态视图
vs = loop.verify_state()
check("verify state", "hit_rate" in vs and len(vs["hit_history"]) == 20, str(len(vs["hit_history"])))
ds = loop.decision_state()
check("decision state", ds["policy"] == "curiosity" and "obs_distribution" in ds, str(ds))
ms = loop.memory_state()
check("memory state", "history_len" in ms and "entities" in ms, str(ms))
gs = loop.graph_state()
check("graph state", "relations" in gs and "entities" in gs, str(gs))
av = loop.audit_view(limit=3)
check("audit view", len(av) == 3 and "L1_perception" in av[0], str(len(av)))

# 7. 单步闭环 + 状态
loop2, p2, w2, r2 = make_loop(budget=1)
loop2.explorer.observe()
loop2.explorer.run(n=loop2.explorer.window)
st = loop2.step()
check("single step", st["tick"] == 1 and all(k in st for k in SevenLayerLoop.LAYERS),
      str(sorted(st.keys())))
st2 = loop2.state()
check("state ok", st2["status"] == "ok" and st2["loop_tick"] == 1
      and st2["audit_len"] == 1, str(st2))

print(f"\nSEVENLAYER result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
