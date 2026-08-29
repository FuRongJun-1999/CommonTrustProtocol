# -*- coding: utf-8 -*-
"""test_world_learner_mcp · 里程碑3.2 world_learner MCP 集成测试（自监督世界学习）"""
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
r1 = eng.world_learner("create", {"size": 24, "trees": 2})
check("create world ok", r1["status"] == "ok" and r1["scene"]["status"] == "ok", str(r1))

# entity
r2 = eng.world_learner("entity", {"category": "player", "behavior": "wander", "pos": [2, 1.5, 2], "speed": 0.5})
check("player added", r2["status"] == "ok" and "entity_id" in r2, str(r2))
pid = r2["entity_id"]
r3 = eng.world_learner("entity", {"category": "wolf", "behavior": "seek", "pos": [15, 1.5, 15], "speed": 0.6, "goal": pid})
check("wolf added", r3["status"] == "ok", str(r3))

# run 数据采集
r4 = eng.world_learner("run", {"n": 12})
check("run ok", r4["status"] == "ok" and r4["run"]["tick"] == 12, str(r4))

# learn 自监督学习
r5 = eng.world_learner("learn", {})
check("learn ok", r5["status"] == "ok" and "per_entity" in r5["learned"]
      and len(r5["learned"]["per_entity"]) == 2, str(r5))

# predict 学得模型预测
r6 = eng.world_learner("predict", {"horizon": 1})
check("predict ok", r6["status"] == "ok" and len(r6["predict"]["predictions"]) == 2
      and all("bound" in p for p in r6["predict"]["predictions"].values()), str(r6))

# evaluate 评估协议（学得 vs naive vs 真模型上界）
r7 = eng.world_learner("evaluate", {"train_ticks": 20, "eval_ticks": 12})
ev = r7["evaluate"]
check("evaluate ok", r7["status"] == "ok" and "learned_rate" in ev
      and "naive_rate" in ev and "oracle_rate" in ev, str(r7))
check("learned beats naive", ev["learned_rate"] > ev["naive_rate"],
      f"learned={ev['learned_rate']} naive={ev['naive_rate']}")

# curve 学习曲线
r8 = eng.world_learner("curve", {"epochs": 3, "per_epoch_ticks": 8, "eval_ticks": 6})
cv = r8["curve"]
check("curve ok", r8["status"] == "ok" and len(cv["curve"]) == 3, str(r8))
check("curve improvement", cv["improvement"] >= 0.0, str(cv["improvement"]))

# masked 遮挡重建损失
r9 = eng.world_learner("masked", {})
check("masked loss", r9["status"] == "ok" and r9["masked"]["loss"] >= 0.0, str(r9))

# model 学得参数导出
r10 = eng.world_learner("model", {})
check("model export", r10["status"] == "ok" and "relations" in r10["model"], str(r10))

# history + state
r11 = eng.world_learner("history", {"limit": 5})
check("history view", r11["status"] == "ok" and len(r11["history"]) > 0, str(r11))
r12 = eng.world_learner("state", {})
check("state ok", r12["status"] == "ok" and r12["learner"]["status"] == "ok", str(r12))

# unknown action
r13 = eng.world_learner("bogus", {})
check("unknown action error", r13["status"] == "error", str(r13))

print(f"\nWORLDLEARNER-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
