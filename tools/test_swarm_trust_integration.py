# -*- coding: utf-8 -*-
"""test_swarm_trust_integration.py · 信任分×协议流集成验证（2026-08-29）

- 正常对端：互验证 pass → 信任上升 → 可继续派单
- 错误产出累积：fail 降信任 → 跌破阈值 → 派单被拒（隔离闭环）
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_m1 import Bus, Node, ProtocolError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="swarm_trust_")
try:
    bus = Bus(os.path.join(tmp, "bus"))
    a = Node("nodeA", bus, ["校验"])
    b = Node("nodeB", bus, ["求和", "坏算"])
    a.attach_remote(b)
    b.register_handler("求和", lambda xs: sum(xs))
    b.register_handler("坏算", lambda xs: sum(xs) + 999)
    b.capabilities.extend(["求和", "坏算"])
    a.hello("nodeB"); b.hello("nodeA")

    t0 = a.trust.score("nodeB")
    a.request_and_execute("nodeB", "求和", [1, 2], verifier=lambda o: (o == 3, "重算=3"))
    check("pass 后信任上升", a.trust.score("nodeB") > t0,
          f"{t0:.2f}→{a.trust.score('nodeB'):.2f}")

    # 反例累积：错误产出 → fail 记录 → 最终隔离
    for i in range(6):
        try:
            a.request_and_execute("nodeB", "坏算", [1, 2],
                                  verifier=lambda o: (o == 3, f"期望 3，实际 {o}"))
        except ProtocolError as e:
            if "信任不足" in str(e):
                check(f"第 {i} 轮后隔离拦截派单", True, str(e)[:50])
                break
    else:
        check("隔离拦截派单", a.trust.isolated("nodeB") and False, "循环结束未拦截")
    check("隔离后直接拒绝派单", a.trust.isolated("nodeB"),
          f"score={a.trust.score('nodeB'):.3f}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"信任×协议流集成: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
