# -*- coding: utf-8 -*-
"""test_spacetime_consistency · 里程碑2.4 时空一致性验证单元测试
（持续运行 + 预测 vs 实际 + 滚动命中率 + 漂移检测 + 自洽判定）"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.spacetime_consistency import SpacetimeConsistency

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 场景 A：确定性世界（seek/follow）→ 应自洽 ----------
stc = SpacetimeConsistency(size=24, window=10, drift_rate=0.7, drift_ticks=3,
                           consistent_rate=0.85, min_consistent_ticks=20)

# 1. 创建场景 + 实体
r0 = stc.create_scene(trees=3, water=True)
check("scene created", r0["status"] == "ok" and r0["blocks"] > 0, str(r0))
p1 = stc.add_entity("player", behavior="seek", pos=(2, 1.5, 2), speed=0.5)
p2 = stc.add_entity("wolf", behavior="seek", pos=(15, 1.5, 15), speed=0.6, goal=p1)
stc.add_path("patrol1", [(5, 1.5, 5), (5, 1.5, 15), (15, 1.5, 15), (15, 1.5, 5)])
stc.add_entity("guard", behavior="follow", pos=(5, 1.5, 5), speed=0.4, goal="patrol1")
check("entities added", len(stc.scene.entities) == 3)

# 2. 持续运行 25 tick（预测 vs 实际 每步验证）
r1 = stc.run(n=25)
check("run advances tick", stc.tick_count == 25, str(stc.tick_count))
check("run reports rolling", r1["rolling_hit_rate"] > 0.0, str(r1))

# 3. 确定性行为精确预测 → 命中率 1.0
det = stc.per_behavior_rates()["deterministic"]
check("deterministic exact hit rate 1.0", det["rate"] == 1.0,
      f"rate={det['rate']} hits={det['hits']}/{det['outcomes']}")

# 4. 滚动命中率窗口跟踪
rl = stc.rolling_hit_rate()
check("rolling in [0,1]", 0.0 <= rl <= 1.0, str(rl))
check("rolling window len", len(stc._rolling) == 10, str(len(stc._rolling)))

# 5. 无漂移 → 无事件
check("no drift events in clean run", len(stc.drift_events()) == 0,
      str(stc.drift_events()))
check("no active drift", not stc.drift_active())

# 6. 不变量保持（界内/落地/有限数）
check("invariants hold", stc._invariant_violations == 0,
      str(stc._invariant_violations))

# 7. 持续运行足够 + 高命中率 → 世界模型自洽
rep = stc.consistency_report()
check("sustained", rep["sustained"], str(rep["tick"]))
check("overall hit rate high", rep["overall_hit_rate"] >= 0.85,
      str(rep["overall_hit_rate"]))
check("verdict self_consistent", rep["verdict"] == "self_consistent",
      rep["verdict"])
check("self_consistent() True", stc.self_consistent(), str(rep))

# 8. 预测历史可审计
hist = stc.prediction_history(limit=3)
check("history entries", len(hist) == 3 and all("outcomes" in h for h in hist),
      str(len(hist)))

# ---------- 场景 B：随机行为（wander/flee）→ 可达域命中，仍自洽 ----------
stc2 = SpacetimeConsistency(size=24, window=10, drift_ticks=3,
                            min_consistent_ticks=20)
stc2.create_scene(trees=2, water=False)
a = stc2.add_entity("rabbit", behavior="wander", pos=(3, 1.5, 3), speed=0.3)
b = stc2.add_entity("fox", behavior="flee", pos=(10, 1.5, 10), speed=0.4, goal=a)
stc2.add_entity("fox2", behavior="flee", pos=(12, 1.5, 12), speed=0.4, goal=a)
stc2.run(n=25)

# 9. 随机行为遵守运动规则 → bounded 命中率高
sto = stc2.per_behavior_rates()["stochastic"]
check("stochastic bounded hit high", sto["rate"] >= 0.9,
      f"rate={sto['rate']} hits={sto['hits']}/{sto['outcomes']}")

# 10. 随机世界同样自洽（模型知道自己随机性边界）
rep2 = stc2.consistency_report()
check("stochastic world self_consistent", rep2["verdict"] == "self_consistent",
      rep2["verdict"] + " rate=" + str(rep2["overall_hit_rate"]))

# ---------- 场景 C：漂移检测（注入不一致 → 自洽破坏） ----------
stc3 = SpacetimeConsistency(size=24, window=10, drift_rate=0.7, drift_ticks=3,
                            consistent_rate=0.85, min_consistent_ticks=20)
stc3.create_scene(trees=2, water=False)
c1 = stc3.add_entity("hero", behavior="seek", pos=(2, 1.5, 2), speed=0.5)
c2 = stc3.add_entity("companion", behavior="seek", pos=(4, 1.5, 4), speed=0.5, goal=c1)
stc3.add_entity("guard", behavior="follow", pos=(5, 1.5, 5), speed=0.4,
                goal="p")
stc3.add_path("p", [(8, 1.5, 8), (12, 1.5, 12)])
stc3.run(n=20)   # 干净运行 → 自洽
check("clean run self_consistent", stc3.self_consistent(),
      stc3.consistency_report()["verdict"])

# 注入不一致：每个 tick 把全部实体瞬移到对角角落（位移远超一切不确定域
# → 每个预测都未命中 → 滚动命中率崩溃 → 漂移检测触发）
for i in range(10):
    corner = (20.0, 1.5, 20.0) if i % 2 == 0 else (2.0, 1.5, 2.0)
    for eid in list(stc3.scene.entities.keys()):
        stc3.teleport(eid, corner)
    stc3.step_verified()

# 11. 漂移检测：注入期间 → drift_active + drift_detected 判定
check("drift active during injection", stc3.drift_active(), "")
rep3 = stc3.consistency_report()
check("verdict drift_detected", rep3["verdict"] == "drift_detected",
      rep3["verdict"])
check("self_consistent False under drift", not stc3.self_consistent(), "")

# 12. 停止注入 → 滚动恢复 → 漂移事件闭合（可审计）
stc3.run(n=20)
check("drift cleared after recovery", not stc3.drift_active(), "")
evs = stc3.drift_events()
check("drift event closed and recorded", len(evs) >= 1, str(evs))
if evs:
    ev = evs[-1]
    check("drift event fields", "start_tick" in ev and "min_rate" in ev
          and "ticks" in ev and "end_tick" in ev, str(ev))
    check("drift event min_rate below threshold", ev["min_rate"] < 0.7,
          str(ev["min_rate"]))
    check("drift event ticks >= drift_ticks", ev["ticks"] >= 3, str(ev["ticks"]))
# 漂移留下历史伤疤：整体命中率跌破自洽阈值 → inconsistent（诚实报告）
rep3b = stc3.consistency_report()
check("scarred world inconsistent (not self_consistent)", 
      rep3b["verdict"] == "inconsistent" and not rep3b["self_consistent"],
      rep3b["verdict"] + " overall=" + str(rep3b["overall_hit_rate"]))

# ---------- 场景 D：一致性恢复（短暂漂移 → 重新自洽） ----------
stc4 = SpacetimeConsistency(size=24, window=5, drift_rate=0.7, drift_ticks=2,
                            min_consistent_ticks=20)
stc4.create_scene(trees=1, water=False)
d1 = stc4.add_entity("seek_a", behavior="seek", pos=(2, 1.5, 2), speed=0.5)
d2 = stc4.add_entity("seek_b", behavior="seek", pos=(4, 1.5, 4), speed=0.5, goal=d1)
stc4.run(n=20)
check("D clean self_consistent", stc4.self_consistent(),
      stc4.consistency_report()["verdict"])
# 短暂不一致（3 tick，两角落交替瞬移 → 位移巨大 → 全部未命中 → 漂移触发）
for i in range(3):
    if i % 2 == 0:
        p1, p2 = (21.0, 1.5, 21.0), (22.0, 1.5, 22.0)
    else:
        p1, p2 = (2.0, 1.5, 2.0), (3.0, 1.5, 3.0)
    stc4.teleport(d1, p1)
    stc4.teleport(d2, p2)
    stc4.step_verified()
check("D drift fired during injection", stc4.drift_active(), "")
check("D not self_consistent under drift", not stc4.self_consistent(), "")
# 停止注入 → 一致性恢复 → 重新自洽
stc4.run(n=15)
check("D drift cleared after recovery", not stc4.drift_active(), "")
check("D drift event recorded", len(stc4.drift_events()) >= 1,
      str(stc4.drift_events()))
rep4 = stc4.consistency_report()
check("D recovered self_consistent", rep4["verdict"] == "self_consistent"
      and rep4["self_consistent"], rep4["verdict"] + " overall="
      + str(rep4["overall_hit_rate"]))

print(f"\nSPACETIME result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
