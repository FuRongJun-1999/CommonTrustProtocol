# -*- coding: utf-8 -*-
"""test_swarm_m1_v2.py · M1 批次 2 验证用例（V-M1.4~1.6，2026-08-29）"""
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


tmp = tempfile.mkdtemp(prefix="swarm_m1b2_")
try:
    bus = Bus(os.path.join(tmp, "bus"))
    a = Node("nodeA", bus, ["校验"])
    b = Node("nodeB", bus, ["求和"])
    a.attach_remote(b)
    b.register_handler("求和", lambda xs: sum(xs))
    a.hello("nodeB")
    b.hello("nodeA")

    # ============ V-M1.4 资格先于执行 ============
    # 未协商能力直接请求执行 → 协议层拒绝（B 对未注册能力判 BLINDSPOT）
    try:
        a.request_and_execute("nodeB", "排序", [3, 1], verifier=lambda o: (True, ""))
        check("V-M1.4 未 ACCEPT 禁止执行", False, "未抛异常")
    except ProtocolError as e:
        check("V-M1.4 未 ACCEPT 禁止执行", "资格不足" in str(e), str(e))

    # ============ V-M1.5 互验证闭环 ============
    # A 请求 B 的求和；A 用**己方基底**（独立重算）裁决 B 的产出
    def a_verifier(output):
        expected = 6  # A 自己算的答案（不信任 B 的过程，只验结果）
        return output == expected, f"A 己方基底重算=6，B 报告={output}"

    r = a.request_and_execute("nodeB", "求和", [1, 2, 3], verifier=a_verifier)
    check("V-M1.5 RESULT 产出正确", r["output"] == 6, f"got {r}")
    check("V-M1.5 A 裁决 pass", r["pass"] is True and "6" in r["evidence"], f"got {r}")
    check("V-M1.5 A 有 ADOPTED 记录", len(a.adopted) == 1 and a.adopted[0]["peer"] == "nodeB",
          f"got {a.adopted}")
    check("V-M1.5 B 有 ADOPTED 记录", len(b.adopted) == 1 and b.adopted[0]["peer"] == "nodeA",
          f"got {b.adopted}")

    # 反向：B 产出错误 → A 裁决 fail → 双方无 ADOPTED 增长
    b.register_handler("坏求和", lambda xs: sum(xs) + 999)
    b.capabilities.append("坏求和")
    r2 = a.request_and_execute("nodeB", "坏求和", [1, 2, 3],
                               verifier=lambda o: (o == 6, f"期望 6，实际 {o}"))
    check("V-M1.5 错误产出裁决 fail", r2["pass"] is False, f"got {r2}")
    check("V-M1.5 fail 不固化", len(a.adopted) == 1 and len(b.adopted) == 1,
          f"A={len(a.adopted)} B={len(b.adopted)}")

    # ============ 批次 3（M2 预备）：ADOPTED 记忆钩子 ============
    hooks = {"a": [], "b": []}
    a.memory_hook = lambda rec: hooks["a"].append(rec)
    b.memory_hook = lambda rec: hooks["b"].append(rec)
    r3 = a.request_and_execute("nodeB", "求和", [4, 5, 6],
                               verifier=lambda o: (o == 15, f"A 重算=15，B 报告={o}"))
    check("批次3 A 侧钩子固化", len(hooks["a"]) == 1 and hooks["a"][0]["output"] == 15,
          f"got {hooks['a']}")
    check("批次3 B 侧钩子固化", len(hooks["b"]) == 1, f"got {hooks['b']}")

    # ============ V-M1.6 端到端消息序列可追溯 ============
    types = [m["type"] for m in a.log]
    check("V-M1.6 完整消息序列", all(t in types for t in
          ("HELLO", "CAP_QUERY", "CAP_REPLY", "TASK", "RESULT", "VERDICT")),
          f"types={types}")
    check("V-M1.6 消息含 reply_to 链", any("reply_to" in m for m in a.log))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"M1 批次 2 验证用例: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
