# -*- coding: utf-8 -*-
"""test_world_server_mcp · 里程碑2.2 world_server MCP 集成测试"""
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

# init 服务器
r1 = eng.world_server("init", {"size": 16})
check("init ok", r1["status"] == "ok" and ("server" in r1 or "world" in r1), str(r1))

# spawn 实体
r2 = eng.world_server("spawn", {"category": "player", "pos": [2, 1.5, 2], "velocity": [0.5, 0, 0]})
check("spawn ok", r2["status"] == "ok" and "entity_id" in r2, str(r2))
eid = r2["entity_id"]

# tick 多路并行
r3 = eng.world_server("tick", {"n": 3})
check("tick ok", r3["status"] == "ok" and r3["tick"]["tick"] == 3, str(r3))

# snapshot（世界记忆）
r4 = eng.world_server("snapshot", {"tag": "checkpoint"})
check("snapshot ok", r4["status"] == "ok" and "snapshot_id" in r4, str(r4))
sid = r4["snapshot_id"]

# feedback（行动反馈）
r5 = eng.world_server("feedback", {"entity_id": eid, "action": "move", "result": "ok"})
check("feedback ok", r5["status"] == "ok" and r5["feedback"]["ok"], str(r5))

# sync（客户端同步）
r6 = eng.world_server("sync", {"client": "client_A"})
check("sync ok", r6["status"] == "ok" and r6["world"]["client"] == "client_A", str(r6))

# verify（预测验证）
r7 = eng.world_server("verify", {"horizon": 2})
check("verify ok", r7["status"] == "ok" and "hit_rate" in r7["verification"], str(r7))

# rollback（错误回滚）
eng.world_server("tick", {"n": 5})
r8 = eng.world_server("rollback", {})
check("rollback ok", r8["status"] == "ok", str(r8))

print(f"\nSERVER-MCP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
