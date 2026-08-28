# -*- coding: utf-8 -*-
"""test_swarm_m2_bridge.py · M2 第一步验证（2026-08-29）

G4 共享成立的第一块：互联成果（ADOPTED）经 memory_hook 固化进灵枢记忆
且可检索。用临时 db（不污染主库）。
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_m1 import Bus, Node
from swarm_m2_bridge import bind_memory, adopted_from_memory
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


tmp = tempfile.mkdtemp(prefix="swarm_m2_")
try:
    # 独立演示库（临时 db，桥接后即删）
    agent = Agent(identity="蜂群A", db_path=os.path.join(tmp, "m2_test.db"))
    bus = Bus(os.path.join(tmp, "bus"))
    a = Node("nodeA", bus, ["校验"])
    b = Node("nodeB", bus, ["求和"])
    a.attach_remote(b)
    b.register_handler("求和", lambda xs: sum(xs))
    a.hello("nodeB")
    b.hello("nodeA")

    # 绑定：A 的互联成果固化进灵枢记忆
    bind_memory(agent, a, "nodeA-ZCode")
    r = a.request_and_execute("nodeB", "求和", [1, 2, 3],
                              verifier=lambda o: (o == 6, f"A 重算=6，B 报告={o}"))
    check("互联闭环 pass", r["pass"] is True, f"got {r}")

    # 固化可检索（G4 第一块）
    hits = adopted_from_memory(agent, "nodeA-ZCode")
    check("ADOPTED 固化进灵枢记忆", len(hits) == 1, f"got {len(hits)} 条")
    check("固化内容含对端与 verdict", hits and "nodeB" in hits[0] and "verdict" in hits[0],
          f"got {hits[:1]}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"M2 桥接验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
