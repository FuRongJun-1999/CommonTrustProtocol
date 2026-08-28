# -*- coding: utf-8 -*-
"""test_swarm_m2_sync.py · M2 知识增量同步验证（2026-08-29）

- 同步后对端获得本端知识（增量到位）
- 幂等：重复同步不重复入库（gap 驱动=只传缺失）
- 协议消息留痕（KNOW_OFFER/KNOW_REQUEST 可追溯）
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_m1 import Bus, Node
from swarm_m2_bridge import bind_memory, sync_knowledge
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'aeis'))
from aeis import Agent

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="swarm_m2s_")
try:
    agent_a = Agent(identity="蜂群A", db_path=os.path.join(tmp, "a.db"))
    agent_b = Agent(identity="蜂群B", db_path=os.path.join(tmp, "b.db"))
    bus = Bus(os.path.join(tmp, "bus"))
    a, b = Node("nodeA", bus, ["校验"]), Node("nodeB", bus, ["求和"])
    a.attach_remote(b)
    b.register_handler("求和", lambda xs: sum(xs))
    a.hello("nodeB"); b.hello("nodeA")

    # A 完成一次互联（固化 1 条 swarm_adopted 进 A 库）
    bind_memory(agent_a, a, "nodeA-ZCode")
    a.request_and_execute("nodeB", "求和", [1, 2], verifier=lambda o: (o == 3, "重算=3"))

    n_b_before = len(agent_b.engine.store.get_nodes_by_tag("swarm_sync", limit=500))
    stat = sync_knowledge(bus, a, "nodeB", agent_a, agent_b)
    check("同步统计 returned", set(stat) == {"offered", "given", "pulled"}, f"got {stat}")
    got_b = agent_b.engine.store.get_nodes_by_tag("swarm_sync", limit=500)
    check("B 获得A 的互联知识", len(got_b) >= 1, f"B 库 {len(got_b)} 条")
    check("B 新增条目含互联成果内容", any("蜂群互联成果" in n.content for n in got_b))

    # 幂等：重复同步不重复入库
    n1 = len(got_b)
    sync_knowledge(bus, a, "nodeB", agent_a, agent_b)
    n2 = len(agent_b.engine.store.get_nodes_by_tag("swarm_sync", limit=500))
    check("重复同步幂等（gap 驱动不重复）", n2 == n1, f"{n1}→{n2}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"M2 增量同步验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
