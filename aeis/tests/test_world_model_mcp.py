# -*- coding: utf-8 -*-
"""test_world_model_mcp · 里程碑3.1 world_model MCP 集成测试（统一世界模型骨干）"""
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
r1 = eng.world_model("create", {"size": 24, "trees": 2})
check("create world ok", r1["status"] == "ok" and r1["scene"]["status"] == "ok", str(r1))

# entity 物理世界添加自主实体
r2 = eng.world_model("entity", {"category": "player", "behavior": "seek", "pos": [2, 1.5, 2], "speed": 0.5})
check("player added", r2["status"] == "ok" and "entity_id" in r2, str(r2))
pid = r2["entity_id"]
r3 = eng.world_model("entity", {"category": "wolf", "behavior": "seek", "pos": [15, 1.5, 15], "speed": 0.6, "goal": pid})
check("wolf added", r3["status"] == "ok", str(r3))
r4 = eng.world_model("entity", {"category": "rabbit", "behavior": "wander", "pos": [10, 1.5, 10], "speed": 0.5})
check("rabbit added", r4["status"] == "ok", str(r4))

# perceive 理解端口
r5 = eng.world_model("perceive", {})
check("perceive ok", r5["status"] == "ok" and r5["perceive"]["observed"] == 3, str(r5))

# generate 生成端口
r6 = eng.world_model("generate", {"horizon": 1})
check("generate predictions", r6["status"] == "ok"
      and len(r6["generate"]["predictions"]) == 3, str(r6))

# run 持续运行（generate→演化→perceive→verify）
r7 = eng.world_model("run", {"n": 20})
check("run ok", r7["status"] == "ok" and r7["run"]["status"] == "ok"
      and r7["run"]["tick"] >= 20, str(r7))

# patterns 观测-only 模式推断
r8 = eng.world_model("patterns", {})
pat = r8["patterns"]
check("patterns ok", r8["status"] == "ok" and "relations" in pat
      and "speed_estimates" in pat and "behavior_inference" in pat, str(r8))

# verify 验证端口
r9 = eng.world_model("verify", {})
check("verify hit_rate", r9["status"] == "ok" and "hit_rate" in r9["verify"],
      str(r9))

# anomalies 预测-观测异常（注入外部事件：瞬移 → 下一 perceive 检测）
eng.world_model("generate", {})
# 直接瞬移物理世界实体（外部事件）
eng._wmodel.world.entities[pid].pos = (20.0, 1.5, 20.0)
r10 = eng.world_model("perceive", {})
check("anomaly detected via mcp", r10["status"] == "ok"
      and r10["perceive"]["anomaly_events"] == 1, str(r10))
r11 = eng.world_model("anomalies", {"limit": 5})
check("anomalies listed", r11["status"] == "ok" and len(r11["anomalies"]) >= 1,
      str(r11))

# graph 世界图
r12 = eng.world_model("graph", {})
check("graph export", r12["status"] == "ok" and r12["graph"]["node_count"] == 3
      and "conditions" in list(r12["graph"]["nodes"].values())[0], str(r12))

# history + state
r13 = eng.world_model("history", {"limit": 5})
check("history view", r13["status"] == "ok" and len(r13["history"]) > 0, str(r13))
r14 = eng.world_model("state", {})
check("state ok", r14["status"] == "ok" and r14["model"]["status"] == "ok", str(r14))

# unknown action
r15 = eng.world_model("bogus", {})
check("unknown action error", r15["status"] == "error", str(r15))

print(f"\nWORLDMODEL-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
