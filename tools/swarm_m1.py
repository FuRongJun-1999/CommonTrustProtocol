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

MSG_TYPES = {"HELLO", "CAP_QUERY", "CAP_REPLY", "TASK", "RESULT", "VERDICT", "ADOPTED"}
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

    def handle_bus(self) -> None:
        """处理收件箱中可响应的请求（CAP_QUERY→CAP_REPLY 四态裁决）。"""
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


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "data", "swarm_bus_demo")
    bus = Bus(root)
    a, b = Node("nodeA", bus, ["排序", "求和"]), Node("nodeB", bus, ["编译"])
    a.attach_remote(b)
    a.hello("nodeB")
    print("A 能力协商 排序:", a.query_capability("nodeB", "编译"))
    print("A 能力协商 存储:", a.query_capability("nodeB", "存储"))
    print("A 记录的 B 边界:", a.blindspots)
