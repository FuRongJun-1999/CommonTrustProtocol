# -*- coding: utf-8 -*-
"""test_swarm_m1.py · M1 批次 1 验证用例（V-M1.1~1.3，2026-08-29）

对照 docs/T12_M1两节点互联详细设计_v0.1.md §五。
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_m1 import make_msg, validate_msg, Bus, Node, ProtocolError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="swarm_m1_")
try:
    # ============ V-M1.1 消息字段校验 ============
    try:
        validate_msg({"type": "HELLO", "from": "A"})
        check("V-M1.1 缺字段报错", False, "未抛异常")
    except ProtocolError as e:
        check("V-M1.1 缺字段报错", "缺字段" in str(e), str(e))
    try:
        make_msg("BAD_TYPE", "A", "B", {})
        check("V-M1.1 非法 type 报错", False, "未抛异常")
    except ProtocolError:
        check("V-M1.1 非法 type 报错", True)
    try:
        make_msg("CAP_QUERY", "A", "B", {})  # 缺 capability
        check("V-M1.1 CAP_QUERY 缺 capability 报错", False, "未抛异常")
    except ProtocolError:
        check("V-M1.1 CAP_QUERY 缺 capability 报错", True)
    try:
        make_msg("CAP_REPLY", "A", "B", {"verdict": "MAYBE", "reason": "x"})
        check("V-M1.1 verdict 非法报错", False, "未抛异常")
    except ProtocolError:
        check("V-M1.1 verdict 非法报错", True)

    # ============ V-M1.2 HELLO 收敛 ============
    bus = Bus(os.path.join(tmp, "bus"))
    a = Node("nodeA", bus, ["排序", "求和"])
    b = Node("nodeB", bus, ["编译"])
    a.attach_remote(b)
    a.hello("nodeB")
    b.hello("nodeA")
    a.poll()  # 收敛：B 的 HELLO 此刻才到达 A（异步消息同步收敛点）
    check("V-M1.2 A 知道 B 能力", a.peers.get("nodeB") == ["编译"], f"got {a.peers}")
    check("V-M1.2 B 知道 A 能力", b.peers.get("nodeA") == ["排序", "求和"], f"got {b.peers}")

    # ============ V-M1.3 四态协商 + 盲区边界 ============
    r1 = a.query_capability("nodeB", "编译")
    check("V-M1.3 已注册能力 ACCEPT", r1["verdict"] == "ACCEPT", f"got {r1}")
    r2 = a.query_capability("nodeB", "存储")
    check("V-M1.3 未注册能力 BLINDSPOT（不猜测）", r2["verdict"] == "BLINDSPOT", f"got {r2}")
    check("V-M1.3 A 记录 B 能力边界", a.blindspots == ["存储"], f"got {a.blindspots}")
    check("V-M1.3 CAP_REPLY 带 reason（可解释）", "reason" in r1 and "reason" in r2)

    # 消息序列可追溯（log 完整）
    check("V-M1.3 消息序列可追溯", len(a.log) >= 4 and a.log[0]["type"] in ("HELLO", "CAP_QUERY"),
          f"log types={[m['type'] for m in a.log]}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"M1 批次 1 验证用例: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
