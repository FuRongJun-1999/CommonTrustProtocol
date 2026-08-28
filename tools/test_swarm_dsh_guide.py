# -*- coding: utf-8 -*-
"""test_swarm_dsh_guide.py · 接入指南合规性验证（2026-08-29）

用**指南 §五骨架独立实现**的 B 节点（不 import swarm_m1 的 Node 逻辑）接入
A 侧完整协议栈，跑通 HELLO→协商→TASK→RESULT→VERDICT 闭环——
证明指南足够 dsh 端独立实现（不依赖主仓库 Node 类）。
"""
import sys, os, shutil, tempfile, json, time, uuid
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_m1 import Bus, Node

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


# ============ 按指南骨架独立实现的 B 节点（~40 行，零主仓库依赖） ============
class GuideB:
    """dsh 端最小 B 节点：严格按 docs/T12_dsh端接入指南_v0.1.md 实现。"""

    def __init__(self, root, me="nodeB"):
        self.root, self.me = root, me
        self.capabilities = ["求和"]
        self.handlers = {"求和": lambda xs: sum(xs)}
        self.adopted = []
        self.peer_caps = {}
        self.log = []

    def send(self, msg):
        d = os.path.join(self.root, msg["to"], "inbox")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, msg["id"] + ".json"), "w", encoding="utf-8") as f:
            json.dump(msg, f, ensure_ascii=False)

    def poll(self):
        d = os.path.join(self.root, self.me, "inbox")
        os.makedirs(d, exist_ok=True)
        for name in sorted(os.listdir(d)):
            p = os.path.join(d, name)
            with open(p, encoding="utf-8") as f:
                msg = json.load(f)
            os.remove(p)
            self.log.append(msg)
            t = msg["type"]
            if t == "HELLO":
                self.peer_caps[msg["from"]] = msg["payload"]["capabilities"]
                self.send({"type": "HELLO", "from": self.me, "to": msg["from"],
                           "id": f"m{uuid.uuid4().hex[:12]}", "ts": time.time(),
                           "payload": {"capabilities": self.capabilities}})
            elif t == "CAP_QUERY":
                cap = msg["payload"]["capability"]
                verdict = "ACCEPT" if cap in self.capabilities else "BLINDSPOT"
                reason = (f"{self.me} 已注册能力: {cap}" if verdict == "ACCEPT"
                          else f"{self.me} 未注册能力: {cap}（能力边界诚实声明）")
                self.send({"type": "CAP_REPLY", "from": self.me, "to": msg["from"],
                           "id": f"m{uuid.uuid4().hex[:12]}", "ts": time.time(),
                           "reply_to": msg["id"],
                           "payload": {"verdict": verdict, "reason": reason}})
            elif t == "TASK":
                out = self.handlers[msg["payload"]["capability"]](msg["payload"]["input"])
                self.send({"type": "RESULT", "from": self.me, "to": msg["from"],
                           "id": f"m{uuid.uuid4().hex[:12]}", "ts": time.time(),
                           "reply_to": msg["id"],
                           "payload": {"output": out, "basis": "dsh 端求和执行器"}})
            elif t == "VERDICT" and msg["payload"]["pass"]:
                self.adopted.append(msg)


tmp = tempfile.mkdtemp(prefix="swarm_guide_")
try:
    root = os.path.join(tmp, "bus")
    a = Node("nodeA", Bus(root), ["校验"])
    b = GuideB(root)                    # 指南骨架 B（非 swarm_m1.Node！）
    b.handle_bus = b.poll               # 接入适配：指南方法名 → A 侧同步通道
    a._remote_side = b                  # A 的同步协商通道指向 GuideB
    a.hello("nodeB")
    b.poll()                            # B 收 HELLO 并回
    a.poll()
    check("指南 B 能力表被 A 收敛", a.peers.get("nodeB") == ["求和"], f"got {a.peers}")

    r = a.request_and_execute("nodeB", "求和", [2, 3, 5],
                              verifier=lambda o: (o == 10, f"A 重算=10，B 报告={o}"))
    check("指南 B 通过协商与执行", r["pass"] is True and r["output"] == 10, f"got {r}")
    check("指南 B 登记 ADOPTED", len(b.adopted) == 1, f"got {len(b.adopted)}")

    # 未注册能力 → 指南 B 回 BLINDSPOT（三纪律之盲区诚实）
    try:
        a.request_and_execute("nodeB", "编译", "x", verifier=lambda o: (True, ""))
        check("指南 B 盲区诚实", False, "未抛异常")
    except Exception as e:
        check("指南 B 盲区诚实", "BLINDSPOT" in str(e), str(e)[:60])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"接入指南合规性验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
