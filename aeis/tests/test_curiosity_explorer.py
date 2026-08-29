# -*- coding: utf-8 -*-
"""test_curiosity_explorer · 里程碑3.3 好奇驱动探索单元测试
（有限带宽主动观测 · 信息增益最大化 · 策略对比 · 涌现的信息瓶颈聚焦）"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.curiosity_explorer import CuriosityExplorer

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 1. 有限带宽观测（传感器子集） ----------
ex = CuriosityExplorer._build_world()
r = ex.observe(entities=list(ex.world.entities.keys())[:2])
check("subset observe", r["status"] == "ok" and r["observed"] == 2, str(r))
check("only chosen updated", ex.nodes.get(list(ex.world.entities.keys())[2]) is None
      or ex.nodes[list(ex.world.entities.keys())[2]].first_seen == 0, "")

# ---------- 2. 信息增益（好奇心） ----------
ex2 = CuriosityExplorer._build_world()
ex2.observe()
ex2.run(n=ex2.window)   # 预热：关系成形
igs = {eid: ex2._info_gain(eid) for eid in ex2.nodes}
check("info gain positive", all(v > 0 for v in igs.values()), str(igs))
names = {eid: n.category for eid, n in ex2.nodes.items()}
wolf = [eid for eid, n in ex2.nodes.items() if n.category == "wolf"][0]
rabbit = [eid for eid, n in ex2.nodes.items() if n.category == "rabbit"][0]
player = [eid for eid, n in ex2.nodes.items() if n.category == "player"][0]
check("bottleneck ig (wolf/player > rabbit)",
      igs[wolf] > igs[rabbit] and igs[player] > igs[rabbit],
      f"wolf={igs[wolf]} player={igs[player]} rabbit={igs[rabbit]}")

# ---------- 3. 好奇探索循环（决策日志可审计） ----------
ex3 = CuriosityExplorer._build_world()
ex3.observe()
ex3.run(n=ex3.window)
entry = ex3.explore_tick(budget=2, policy="curiosity")
check("explore log entry", "chosen" in entry and "ig_scores" in entry
      and "mean_bound" in entry and entry["policy"] == "curiosity", str(entry))
check("chosen count", len(entry["chosen"]) == 2, str(entry["chosen"]))
check("ig scores match chosen", all(c in entry["ig_scores"] for c in entry["chosen"]),
      str(entry["ig_scores"]))

# ---------- 4. 不确定度轨迹（认知缺口收紧） ----------
ex4 = CuriosityExplorer._build_world()
ex4.observe()
ex4.run(n=ex4.window)
res = ex4.explore(ticks=30, budget=2, policy="curiosity")
check("explore ok", res["status"] == "ok" and res["tick"] >= 36, str(res))
curve = ex4.uncertainty_curve
check("uncertainty curve", len(curve) == 30, str(len(curve)))
check("uncertainty reduced (min <= first)",
      min(curve) <= curve[0] + 1e-6, f"min={min(curve)} first={curve[0]}")
check("obs distribution recorded", len(res["obs_distribution"]) == 3, str(res))

# ---------- 5. 策略对比（好奇 vs 随机 vs 轮询，同世界轨迹） ----------
comp = CuriosityExplorer().compare_policies(budget=2, explore_ticks=40, probe_ticks=15)
rc = comp["results"]
check("compare all policies", set(rc.keys()) == {"curiosity", "random", "round_robin"},
      str(rc.keys()))
check("curiosity beats random probe", rc["curiosity"]["probe_rate"] > rc["random"]["probe_rate"],
      f"cury={rc['curiosity']['probe_rate']} rand={rc['random']['probe_rate']}")
check("curiosity beats round_robin probe",
      rc["curiosity"]["probe_rate"] > rc["round_robin"]["probe_rate"],
      f"cury={rc['curiosity']['probe_rate']} rr={rc['round_robin']['probe_rate']}")
check("curiosity lower min uncertainty",
      rc["curiosity"]["uncertainty_min"] < rc["random"]["uncertainty_min"],
      f"cury={rc['curiosity']['uncertainty_min']} rand={rc['random']['uncertainty_min']}")
# 涌现：学习者盯住信息枢纽（wolf=链中段）多于下游叶子（rabbit）
# compare 内世界为新建实例（eid 随机）——按插入序映射 player/wolf/rabbit
od = rc["curiosity"]["obs_distribution"]
ids = list(od.keys())
_pp, _ww, _rr = ids[0], ids[1], ids[2]
check("emergent bottleneck focus (wolf >= rabbit)",
      od[_ww] >= od[_rr], f"wolf={od[_ww]} rabbit={od[_rr]} obs={od}")
check("curiosity probe high", rc["curiosity"]["probe_rate"] >= 0.9,
      str(rc["curiosity"]["probe_rate"]))

# ---------- 6. 探针评估 + 好奇心摘要 ----------
ex5 = CuriosityExplorer._build_world()
ex5.observe()
ex5.run(n=ex5.window)
ex5.explore(ticks=20, budget=2, policy="curiosity")
pr = ex5.probe(ticks=10)
check("probe rates", "learned_rate" in pr and "naive_rate" in pr
      and pr["outcomes"] >= 20, str(pr))
summ = ex5.curiosity_summary()
check("curiosity summary", "observations" in summ and "uncertainty_trend" in summ,
      str(summ))
log = ex5.exploration_log_view(limit=3)
check("exploration log view", len(log) == 3 and "tick" in log[0], str(len(log)))
st = ex5.state()
check("state ok", st["status"] == "ok" and st["exploration_steps"] == 20, str(st))

print(f"\nCURIOSITY result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
