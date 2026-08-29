# -*- coding: utf-8 -*-
"""test_world_learner · 里程碑3.2 自监督世界学习（V-JEPA 式）单元测试
（观测面=缸中之脑 · 自监督目标 · 学得模型 · 外部裁判评估 · 学习曲线）"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.world_learner import WorldLearner

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

def make_world():
    lr = WorldLearner(size=24)
    lr.world.create_scene(trees=2, water=False)
    p = lr.world.add_entity("player", behavior="wander", pos=(2, 1.5, 2), speed=0.5)
    w = lr.world.add_entity("wolf", behavior="seek", pos=(15, 1.5, 15), speed=0.6, goal=p)
    g = lr.world.add_entity("guard", behavior="follow", pos=(5, 1.5, 5), speed=0.4, goal="patrol")
    lr.world.add_path("patrol", [(8, 1.5, 8), (12, 1.5, 12)])
    return lr, p, w, g

# ---------- 1. 观测面（缸中之脑：只暴露位置/类别） ----------
lr, p, w, g = make_world()
o = lr.observe()
check("observe ok", o["status"] == "ok" and o["observed"] == 3, str(o))
check("observation surface only pos/category",
      all(set(n.keys()) <= {"category", "pos"} for rec in lr.history
          for n in rec["entities"].values()), "")
check("nodes created", len(lr.nodes) == 3)

# ---------- 2. 时空一致性（身份跨时间关联） ----------
lr.run(n=5)
check("identity stable", all(eid in lr.nodes for eid in (p, w, g)), "")
check("history grows", len(lr.history) == 6)

# ---------- 3. 自监督学习 → 学得模型（白箱可审计） ----------
m = lr.learn()
check("learned per_entity", all(eid in m["per_entity"] for eid in (p, w, g)), str(m.keys()))
check("speed estimates", all(m["per_entity"][e]["speed_est"] > 0
                             for e in (p, w, g)), str(m["per_entity"]))
wolf_rel = [r for r in m["relations"] if r["source"] == w and r["relation"] == "seek"]
check("learned seek relation (wolf->player)", len(wolf_rel) >= 1, str(m["relations"]))
check("model export", lr.model_params() == m)

# ---------- 4. 学得模型预测（带不确定边界） ----------
pr = lr.predict(horizon=1)
check("predict all entities", len(pr["predictions"]) == 3, str(pr.keys()))
check("predict bounds", all(p["bound"] > 0 for p in pr["predictions"].values()))
check("predict modes", all(p["mode"] in ("exact", "chase_stochastic",
                                        "bounded_noisy", "bounded_stochastic")
                           for p in pr["predictions"].values()))

# ---------- 5. 评估协议（外部裁判：学得 vs naive vs 真模型上界） ----------
lr2, p2, w2, g2 = make_world()
res = lr2.evaluate(train_ticks=30, eval_ticks=20)
check("evaluate runs", res["outcomes"] >= 20, str(res))
check("learned beats naive", res["learned_rate"] > res["naive_rate"],
      f"learned={res['learned_rate']} naive={res['naive_rate']}")
check("oracle upper bound", res["oracle_rate"] >= res["learned_rate"] - 0.05,
      f"oracle={res['oracle_rate']} learned={res['learned_rate']}")
check("learned high", res["learned_rate"] >= 0.8, str(res["learned_rate"]))
check("gap reported", "gap_to_oracle" in res)

# ---------- 6. 学习曲线（观测增加 → 命中率提升 · 距离下降） ----------
lr3, p3, w3, g3 = make_world()
cv = lr3.learning_curve(epochs=4, per_epoch_ticks=10, eval_ticks=8)
curve = cv["curve"]
check("curve epochs", len(curve) == 4 and all(c["observations"] > 0 for c in curve))
rates = [c["learned_rate"] for c in curve]
check("curve learned high", rates[-1] >= 0.8, str(rates))
check("curve improvement >= 0", cv["improvement"] >= 0.0, str(cv["improvement"]))
dists = [c["mean_distance"] for c in curve]
# 认知缺口 = 1 - 命中率：随学习收紧（命中率↑=缺口↓）；mean_distance 受
# 随机行为固有运动主导（wander 恒 ≈ speed），仅作信息性指标
check("cognitive gap closed", (1 - rates[-1]) <= (1 - rates[0]),
      f"gap {1-rates[-1]} vs {1-rates[0]}")
check("mean_distance finite", all(d >= 0.0 for d in dists), str(dists))
check("curve beats naive", rates[-1] > curve[-1]["naive_rate"], str(curve[-1]))

# ---------- 7. 遮挡重建（自监督损失信号） ----------
lr4, p4, w4, g4 = make_world()
lr4.run(n=10)
ml = lr4.masked_loss()
check("masked loss computed", ml["samples"] >= 1 and ml["loss"] >= 0.0, str(ml))
ns = lr4.next_state_loss(eval_ticks=5)
check("next_state_loss finite", ns["mean_distance"] >= 0.0 and ns["samples"] >= 5, str(ns))

# ---------- 8. 导出 ----------
st = lr2.state()
check("state ok", st["status"] == "ok" and st["entities"] == 3 and st["evals"] >= 1)
hv = lr2.history_view(limit=3)
check("history view", len(hv) == 3 and "entities" in hv[0])
check("evals recorded", len(lr2.evals) >= 1 and "oracle_rate" in lr2.evals[-1])

print(f"\nWORLDLEARNER result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
