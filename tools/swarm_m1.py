# Copyright 2026 灵枢 (Lingshu) · MIT
"""swarm_m1.py · 蜂群 M1 两节点最小互联——批次 1（2026-08-29 心跳）

依 docs/T12_M1两节点互联详细设计_v0.1.md。协议角色实现（先协议正确性，
后真实接入）：
- Msg：七类协议消息构造/校验（缺字段/非法 type 显式报错）
- Bus：目录总线（data/swarm_bus/<node>/inbox/*.json，教学模拟口径）
- Node：能力注册表 + 四态协商（CAP_QUERY→CAP_REPLY）+ BLINDSPOT 边界记录

白箱三纪律（设计文档 §二）：
- 资格先于执行（TASK 仅 ACCEPT 后合法——批次 2 实现 TASK 分派时强制）
- 自验证不采信（VERDICT 由接收方裁决——批次 2）
- BLINDSPOT 记边界不重试猜测（本批即实现）
"""

from __future__ import annotations

import json
import os
import time
import uuid

MSG_TYPES = {"HELLO", "CAP_QUERY", "CAP_REPLY", "TASK", "RESULT", "VERDICT", "ADOPTED",
             "KNOW_OFFER", "KNOW_REQUEST", "KNOW_GIVE"}  # M2：知识增量同步三消息
_VERDICTS = {"ACCEPT", "REJECT", "DEFER", "BLINDSPOT"}


class ProtocolError(Exception):
    """M1 协议白箱错误（字段缺失/type 非法/资格违规）。"""


def make_msg(mtype: str, sender: str, receiver: str, payload: dict,
             reply_to: str | None = None) -> dict:
    """构造协议消息（自动 id/ts；字段缺失在 validate 前即拦截）。"""
    if mtype not in MSG_TYPES:
        raise ProtocolError(f"非法消息类型: {mtype}（允许: {sorted(MSG_TYPES)}）")
    msg = {"type": mtype, "from": sender, "to": receiver,
           "id": f"m{uuid.uuid4().hex[:12]}", "ts": round(time.time(), 3),
           "payload": payload}
    if reply_to:
        msg["reply_to"] = reply_to
    validate_msg(msg)
    return msg


def validate_msg(msg: dict) -> None:
    """V-M1.1 消息字段校验：必填字段/type/payload 形态，显式报错。"""
    for key in ("type", "from", "to", "id", "ts", "payload"):
        if key not in msg:
            raise ProtocolError(f"消息缺字段: {key}（msg={msg}）")
    if msg["type"] not in MSG_TYPES:
        raise ProtocolError(f"非法消息类型: {msg['type']}")
    if not isinstance(msg["payload"], dict):
        raise ProtocolError(f"payload 须为 dict，得到 {type(msg['payload']).__name__}")
    if msg["type"] == "CAP_QUERY" and "capability" not in msg["payload"]:
        raise ProtocolError("CAP_QUERY 缺 capability")
    if msg["type"] == "CAP_REPLY":
        if msg["payload"].get("verdict") not in _VERDICTS:
            raise ProtocolError(f"CAP_REPLY verdict 非法: {msg['payload'].get('verdict')!r}"
                                f"（允许: {sorted(_VERDICTS)}）")
        if "reason" not in msg["payload"]:
            raise ProtocolError("CAP_REPLY 缺 reason（裁决须可解释）")
    if msg["type"] in ("KNOW_OFFER", "KNOW_REQUEST"):
        if not isinstance(msg["payload"].get("entries"), list):
            raise ProtocolError(f"{msg['type']} 缺 entries 列表")
    if msg["type"] == "KNOW_GIVE" and "knowledge" not in msg["payload"]:
        raise ProtocolError("KNOW_GIVE 缺 knowledge 内容")


class Bus:
    """目录总线：每节点一个收件箱目录，发送=写入对方收件箱（教学模拟）。"""

    def __init__(self, root: str):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def _inbox(self, node_id: str) -> str:
        d = os.path.join(self.root, node_id, "inbox")
        os.makedirs(d, exist_ok=True)
        return d

    def send(self, msg: dict) -> None:
        validate_msg(msg)
        path = os.path.join(self._inbox(msg["to"]), msg["id"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(msg, f, ensure_ascii=False)

    def recv(self, node_id: str) -> list[dict]:
        """收取并清空收件箱（按 ts 排序，消息序列可追溯）。"""
        d = self._inbox(node_id)
        out = []
        for name in sorted(os.listdir(d)):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                out.append(json.load(f))
            os.remove(os.path.join(d, name))
        out.sort(key=lambda m: m["ts"])
        return out


class Node:
    """协议节点：能力注册表 + 四态协商 + 盲区边界记录。"""

    def __init__(self, node_id: str, bus: Bus, capabilities: list[str]):
        self.id = node_id
        self.bus = bus
        self.capabilities = list(capabilities)  # 显式能力边界声明（盲区诚实）
        self.peers: dict[str, list[str]] = {}   # HELLO 收敛的对端能力表
        self.blindspots: list[str] = []         # 对端 BLINDSPOT 记录（不重试猜测）
        self.log: list[dict] = []               # 全部收发消息（可追溯）
        # 批次 2：互验证闭环
        self.handlers: dict[str, object] = {}   # capability → 执行函数
        self.granted: set[tuple[str, str]] = set()  # (peer, capability) 已 ACCEPT
        self.verifier: object = None            # 己方验证基底：output → (pass, evidence)
        self.adopted: list[dict] = []           # ADOPTED 固化登记
        # 批次 3（M2 预备）：ADOPTED 事件外挂记忆钩子——互联成果固化进
        # 节点自身知识库（灵枢 remember / 图库 insert），由宿主注入
        self.memory_hook: object = None
        # 批次 4（M3 集成）：信任账本——分工由信任决定（智能论 §2.9）
        from swarm_m3_trust import TrustLedger
        self.trust = TrustLedger()

    def poll(self) -> None:
        """处理收件箱中的 HELLO（能力表收敛）。异步消息的同步收敛点。"""
        for msg in self.bus.recv(self.id):
            self.log.append(msg)
            if msg["type"] == "HELLO":
                self.peers[msg["from"]] = msg["payload"]["capabilities"]

    def hello(self, peer: str) -> None:
        """V-M1.2 HELLO 交换：广播己方能力并登记对端能力表。"""
        self.bus.send(make_msg("HELLO", self.id, peer, {"capabilities": self.capabilities}))
        self.poll()

    def query_capability(self, peer: str, capability: str) -> dict:
        """V-M1.3 跨节点四态协商：发起 CAP_QUERY，同步等待并处理对端回复。"""
        q = make_msg("CAP_QUERY", self.id, peer, {"capability": capability})
        self.bus.send(q)
        self.log.append(q)
        # 对端处理（教学口径同步调用；真实异步批次 2）
        self._remote_side.handle_bus()
        for msg in self.bus.recv(self.id):
            self.log.append(msg)
            if msg["type"] == "CAP_REPLY" and msg.get("reply_to") == q["id"]:
                if msg["payload"]["verdict"] == "BLINDSPOT":
                    self.blindspots.append(capability)  # 记边界，不重试猜测
                return msg["payload"]
        raise ProtocolError("CAP_QUERY 无回复（协议死锁）")

    # ---- 对端侧（由 query_capability 的持有方注入）----

    def attach_remote(self, remote: "Node") -> None:
        """测试/演示用：互设对端引用（同步协商通道）。"""
        self._remote_side = remote
        remote._remote_side = self

    def register_handler(self, capability: str, fn, verifier=None) -> None:
        """注册能力执行函数（+可选验证基底说明）。"""
        self.handlers[capability] = fn
        if verifier:
            self.capabilities.append(capability)

    def request_and_execute(self, peer: str, capability: str, input_data,
                            verifier) -> dict:
        """V-M1.4/1.5：协商→TASK→RESULT→VERDICT→ADOPTED 完整闭环。

        白箱纪律：①资格先于执行（未 ACCEPT 不发 TASK）；②自验证不采信
        （verifier 是 A 的己方基底，裁决 B 的产出）。
        """
        ok, reason = self.trust.can_dispatch(peer)  # M3：信任决定分工
        if not ok:
            raise ProtocolError(f"信任不足：{reason}")
        reply = self.query_capability(peer, capability)
        if reply["verdict"] != "ACCEPT":
            raise ProtocolError(
                f"资格不足：{peer} 对 {capability} 判定 {reply['verdict']}——TASK 禁止发送")
        self.granted.add((peer, capability))
        task = make_msg("TASK", self.id, peer,
                        {"capability": capability, "input": input_data})
        self.bus.send(task)
        self.log.append(task)
        self._remote_side.handle_bus()          # B 执行并回 RESULT
        for msg in self.bus.recv(self.id):
            self.log.append(msg)
            if msg["type"] == "RESULT" and msg.get("reply_to") == task["id"]:
                output = msg["payload"]["output"]
                passed, evidence = verifier(output)   # 己方基底裁决（互验证）
                vd = make_msg("VERDICT", self.id, peer,
                              {"pass": passed, "evidence": evidence},
                              reply_to=msg["id"])
                self.bus.send(vd)
                self.log.append(vd)
                self._remote_side.handle_bus()    # B 登记 ADOPTED
                self.poll()                        # A 收 B 的 ADOPTED 确认
                self.trust.record(peer, passed)  # M3：行为验证后更新信任
                if passed:
                    rec = {"verdict_id": vd["id"], "peer": peer, "output": output}
                    self.adopted.append(rec)
                    if self.memory_hook:  # 批次 3：互联成果固化进自身知识库
                        self.memory_hook(rec)
                return {"output": output, "pass": passed, "evidence": evidence}
        raise ProtocolError("TASK 无 RESULT 回复（协议死锁）")

    def handle_bus_sync(self, self_agent) -> None:
        """M2 同步辅助（接收方处理自己的收件箱，比对/固化均用自己库）：

        - KNOW_OFFER → 比对自身已有指纹 → 回 KNOW_REQUEST（缺失清单）
        - KNOW_GIVE  → 固化进自身库（tag: swarm_sync，幂等由 digest 保证）
        """
        from swarm_m2_bridge import _digest
        have = {_digest(n.content)
                for n in self_agent.engine.store.get_nodes_by_tag("swarm_sync", limit=500)}
        for msg in self.bus.recv(self.id):
            self.log.append(msg)
            if msg["type"] == "KNOW_OFFER":
                missing = [e for e in msg["payload"]["entries"]
                           if e["digest"] not in have]
                if missing:
                    self.bus.send(make_msg("KNOW_REQUEST", self.id, msg["from"],
                                           {"entries": missing}, reply_to=msg["id"]))
            elif msg["type"] == "KNOW_GIVE":
                content = msg["payload"]["knowledge"]
                if _digest(content) not in have:  # 幂等：已有不重复入库
                    self_agent.remember(content=content, importance=0.6,
                                        tags=["swarm_sync", "M2"])
                    have.add(_digest(content))

    def handle_bus(self) -> None:
        """处理收件箱请求：CAP_QUERY 四态裁决 / TASK 执行 / VERDICT 固化。"""
        for msg in self.bus.recv(self.id):
            self.log.append(msg)
            if msg["type"] == "CAP_QUERY":
                cap = msg["payload"]["capability"]
                if cap in self.capabilities:
                    verdict, reason = "ACCEPT", f"{self.id} 已注册能力: {cap}"
                else:
                    verdict = "BLINDSPOT"  # 不猜测：无此能力=诚实声明
                    reason = f"{self.id} 未注册能力: {cap}（能力边界诚实声明）"
                self.bus.send(make_msg("CAP_REPLY", self.id, msg["from"],
                                       {"verdict": verdict, "reason": reason},
                                       reply_to=msg["id"]))
            elif msg["type"] == "TASK":
                cap = msg["payload"]["capability"]
                if (msg["from"], cap) not in self.granted and cap not in self.capabilities:
                    raise ProtocolError(f"资格违规：{msg['from']} 未协商即 TASK（{cap}）")
                if cap not in self.handlers:
                    raise ProtocolError(f"无执行器: {cap}")
                output = self.handlers[cap](msg["payload"]["input"])
                self.bus.send(make_msg("RESULT", self.id, msg["from"],
                                       {"output": output,
                                        "basis": f"{self.id} 以 {cap} 执行器计算"},
                                       reply_to=msg["id"]))
            elif msg["type"] == "VERDICT":
                if msg["payload"]["pass"]:
                    rec = {"verdict_id": msg["id"], "peer": msg["from"],
                           "reply_to": msg.get("reply_to")}
                    self.adopted.append(rec)
                    if self.memory_hook:  # 批次 3：对端同样固化
                        self.memory_hook(rec)


if __name__ == "__main__":
    import sys
    import tempfile
    sys.stdout.reconfigure(encoding="utf-8")
    # 每次运行唯一总线目录（Bus 目录按 node_id 持久，跨实例复用会串消息）
    root = tempfile.mkdtemp(prefix="swarm_m1_demo_")
    bus = Bus(root)
    a = Node("nodeA", bus, ["排序", "校验"])
    b = Node("nodeB", bus, ["求和"])
    a.attach_remote(b)
    b.register_handler("求和", lambda xs: sum(xs))
    print(f"[M1 端到端演示] 节点：{a.id}(灵枢·ZCode) ↔ {b.id}(灵枢·dsh)")
    print("[M1 端到端演示] HELLO 交换…")
    a.hello(b.id)
    b.hello(a.id)
    a.poll()
    print("[M1 端到端演示] A 请求 B 的求和能力，A 用己方基底裁决…")
    r = a.request_and_execute(b.id, "求和", [1, 2, 3, 4],
                              verifier=lambda o: (o == 10, f"A 重算=10，B 报告={o}"))
    print("  结果:", r)
    print("  A adopted:", len(a.adopted), "| B adopted:", len(b.adopted))
    print("  序列:", [m["type"] for m in a.log])
