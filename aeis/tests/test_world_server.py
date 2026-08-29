# -*- coding: utf-8 -*-
"""test_world_server · 里程碑2.2 AI游戏世界服务器单元测试"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.world_server import WorldServer

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

srv = WorldServer(size=16, ground_level=1)
srv.world.build_flatland(trees=0)

# 1. tick 多路并行（多实体独立演化）
pid = srv.world.spawn_entity("player", (2, 1.5, 2), velocity=(0.5, 0, 0))
bid = srv.world.spawn_entity("ball", (8, 1.5, 8), velocity=(-0.3, 0, 0.4))
rid = srv.world.spawn_entity("bird", (10, 3, 10), velocity=(0.2, 0, 0.2))
r1 = srv.tick(n=3)
check("tick advances", r1["tick"] == 3 and r1["entities"] == 3, str(r1))
check("history recorded", len(srv._history) == 3, str(len(srv._history)))

# 2. 多路并行：每个实体独立移动
st = srv.sync()
ents = st["entities"]
check("player moved", ents[pid]["pos"][0] > 2.0, str(ents[pid]["pos"]))
check("ball moved", ents[bid]["pos"][0] < 8.0, str(ents[bid]["pos"]))
check("bird moved", ents[rid]["pos"][2] > 10.0, str(ents[rid]["pos"]))

# 3. 快照/回滚（世界记忆 + 错误回滚）
sid = srv.snapshot("before_crash")
check("snapshot created", sid in srv.snapshots(), str(srv.snapshots()))
# 推进世界（模拟错误状态）
srv.tick(n=5)
before_rollback = srv.tick_count
check("world advanced", before_rollback > 3)
ok = srv.restore(sid)
check("restore ok", ok)
check("tick restored", srv.tick_count == 3, str(srv.tick_count))

# 4. 反馈（实体行动 → 世界响应）
f1 = srv.feedback(pid, "move", "ok")
check("feedback recorded", f1["ok"] and len(srv.feedback_log()) == 1, str(f1))
f2 = srv.feedback("ghost", "jump", "nope")
check("feedback unknown entity", not f2["ok"])

# 5. 同步（客户端状态视图）
sync = srv.sync(client_id="client_A")
check("sync has world view", sync["client"] == "client_A" and sync["tick"] >= 0)
check("sync entities", len(sync["entities"]) == 3)

# 6. 预测验证（时空外推 → 命中判定）
srv2 = WorldServer(size=16, ground_level=1)
srv2.world.build_flatland(trees=0)
srv2.world.spawn_entity("ball", (2, 1.5, 2), velocity=(1.0, 0, 0.5))
vr = srv2.verify_prediction(horizon=3)
check("verify returns stats", "hit_rate" in vr and vr["hits"] + vr["misses"] == 1, str(vr))
check("linear motion predicted hit", vr["hits"] == 1, str(vr))

# 7. rollback 到最近快照
srv3 = WorldServer(size=8, ground_level=1)
srv3.world.build_flatland(trees=0)
srv3.world.spawn_entity("e1", (1, 1.5, 1), velocity=(0.5, 0, 0))
srv3.tick(n=2)
srv3.snapshot("s1")
srv3.tick(n=5)
rb = srv3.rollback()
check("rollback to latest", rb == "s1" and srv3.tick_count == 2, f"{rb} tick={srv3.tick_count}")

print(f"\nSERVER result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
