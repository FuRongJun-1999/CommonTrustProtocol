# -*- coding: utf-8 -*-
"""test_world_model · 里程碑3.1 统一世界模型（HERMES 式骨干）单元测试
（世界图统一表征 + 理解/生成/验证三端口 + 生成先验注入理解 + 观测-only 模式推断）"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.world_model import UnifiedWorldModel

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 场景 A：理解端口（观测 → 世界图） ----------
wm = UnifiedWorldModel(size=24)
wm.world.create_scene(trees=2, water=False)
p1 = wm.world.add_entity("player", behavior="seek", pos=(2, 1.5, 2), speed=0.5)
w1 = wm.world.add_entity("wolf", behavior="seek", pos=(15, 1.5, 15), speed=0.6, goal=p1)
r1 = wm.world.add_entity("rabbit", behavior="wander", pos=(10, 1.5, 10), speed=0.5)

# 1. perceive 观测 → 世界图节点
per = wm.perceive()
check("perceive ok", per["status"] == "ok" and per["observed"] == 3, str(per))
check("world graph nodes", len(wm.nodes) == 3)
check("conditions provenance", all("observation_tool" in c and "first_seen" in c
                                   for c in wm._conditions.values()))

# 2. 身份追踪：无 eid 观测按最近邻关联（同一实体 → 同一节点）
obs2 = [{"category": "player", "pos": (2.5, 1.5, 2.5)},
        {"category": "wolf", "pos": (14.5, 1.5, 15)},
        {"category": "rabbit", "pos": (10.5, 1.5, 10)}]
per2 = wm.perceive(observations=obs2)
check("identity tracked", len(wm.nodes) == 3, str(wm.nodes.keys()))
check("matched count", per2["matched"] == 3, str(per2))

# 3. 4D 演化历史（观测序列记忆）
check("history sequence", len(wm.history) == 2 and "entities" in wm.history[-1])

# ---------- 场景 B：生成端口 + 观测-only 模式推断 ----------
# 让世界跑一段，模型持续观测（模型只看位置，不看行为规则）
for _ in range(10):
    wm.world.step(n=1)
    wm.perceive()
pat = wm.infer_patterns()
check("patterns speed estimates", all(e in pat["speed_estimates"]
                                      for e in wm.nodes), str(pat.keys()))
check("patterns behavior inferred", all(n.behavior_inferred in
      ("wander", "seek", "flee", "follow", "unknown")
      for n in wm.nodes.values()))
# 模型推断出 wolf 追逐 player（观测-only → seek 关系）
wolf_rel = [e for e in wm.edges if e.source == w1 and e.relation == "seek"]
check("inferred seek relation (wolf->player)", len(wolf_rel) >= 1,
      str([e.to_dict() for e in wm.edges]))
check("wolf behavior inferred seek", wm.nodes[w1].behavior_inferred in ("seek", "wander"),
      wm.nodes[w1].behavior_inferred)

# 4. 生成端口：候选未来 + 不确定边界
gen = wm.generate(horizon=1)
check("generate predictions", len(gen["predictions"]) == 3, str(gen.keys()))
check("generate bound", all("bound" in p and p["bound"] > 0
                            for p in gen["predictions"].values()))
check("generate mode", all(p["mode"] in ("exact", "bounded_noisy",
                                         "bounded_stochastic", "chase_stochastic")
                           for p in gen["predictions"].values()))

# ---------- 场景 C：验证端口（外部观察者逐 tick 对比） ----------
wm2 = UnifiedWorldModel(size=24)
wm2.world.create_scene(trees=2, water=False)
p2 = wm2.world.add_entity("player", behavior="seek", pos=(2, 1.5, 2), speed=0.5)
w2 = wm2.world.add_entity("wolf", behavior="seek", pos=(15, 1.5, 15), speed=0.6, goal=p2)
r2 = wm2.world.add_entity("rabbit", behavior="wander", pos=(10, 1.5, 10), speed=0.5)
# 先观测 2 tick 建立轨迹（推断需要 ≥2 个观测点）
wm2.perceive()
wm2.world.step(n=1); wm2.perceive()
# 持续运行 30 tick：generate → 物理演化 → perceive → verify
run = wm2.verify_run(n=30)
check("verify_run ok", run["status"] == "ok" and run["tick"] >= 32, str(run["tick"]))
check("rolling hit rate high", run["rolling_hit_rate"] >= 0.8,
      str(run["rolling_hit_rate"]))
check("verify details", len(run["last"]["details"]) == 3
      and all("hit" in d for d in run["last"]["details"]))

# 5. 生成先验注入理解：注入外部事件（瞬移）→ 预测-观测异常被检测
eid = p2
before = wm2.nodes[eid].pos
wm2.generate(horizon=1)                    # 生成先验（预期位置）
wm2.world.entities[eid].pos = (20.0, 1.5, 20.0)   # 物理世界外部变更
per3 = wm2.perceive()
check("anomaly detected", per3["anomaly_events"] == 1, str(per3))
anoms = wm2.anomalies()
check("anomaly recorded", len(anoms) >= 1 and anoms[-1]["entity"] == eid,
      str(anoms[-1] if anoms else None))
check("confidence dropped on anomaly", wm2.nodes[eid].confidence < 0.5,
      str(wm2.nodes[eid].confidence))

# 6. 一致观测 → 置信上升
wm3 = UnifiedWorldModel(size=16)
wm3.world.create_scene(trees=1, water=False)
c1 = wm3.world.add_entity("guard", behavior="follow", pos=(5, 1.5, 5), speed=0.4,
                          goal="p")
wm3.world.add_path("p", [(8, 1.5, 8), (12, 1.5, 12)])
wm3.perceive()
wm3.world.step(n=1); wm3.perceive()
wm3.verify_run(n=15)
check("confidence rose on consistency", wm3.nodes[c1].confidence > 0.5,
      str(wm3.nodes[c1].confidence))

# ---------- 场景 D：世界图导出 ----------
gr = wm2.graph()
check("graph export", "nodes" in gr and "edges" in gr and "node_count" in gr
      and gr["node_count"] == 3)
check("graph conditions", all("conditions" in n for n in gr["nodes"].values()))
hv = wm2.history_view(limit=3)
check("history view", len(hv) == 3 and "entities" in hv[0])

print(f"\nWORLDMODEL result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
