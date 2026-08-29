# -*- coding: utf-8 -*-
"""swarm_orchestrator.py · 蜂群协作编排层批 1（2026-08-29 心跳）

依 docs/蜂群协作编排层设计_v0.1.md：
- O1 能力目录 Registry：节点动态注册/能力发现/信任查询/心跳过期剔除
- 职责协商：ROLE_OFFER/ROLE_REPLY/ROLE_CONFIRM 三消息 + 租约衰减
  （复用 stable_lease 衰减核 exp(-γ·t)；冲突时信任高者得）

理论依据：智能论 3.4 六实例蜂群映射（结构层参考架构）——
职责不是静态配置，是交流协商的产物（荣定调）。
"""
from __future__ import annotations

import json
import os
import re
import time
import uuid

MSG_ROLE = {"ROLE_OFFER", "ROLE_REPLY", "ROLE_CONFIRM"}
ROLES = {"record", "output", "designer_prep", "verify", "reflect"}  # vitals 不可协商


class ProtocolError(Exception):
    pass


def make_msg(mtype, sender, receiver, payload, reply_to=None):
    if mtype not in MSG_ROLE and mtype not in ("HELLO",):
        # 复用 M1 validate 前的宽松构造（仅职责类在此）
        pass
    m = {"type": mtype, "from": sender, "to": receiver,
         "id": f"r{uuid.uuid4().hex[:12]}", "ts": round(time.time(), 3),
         "payload": payload}
    if reply_to:
        m["reply_to"] = reply_to
    return m


class Registry:
    """O1 能力目录：节点注册/能力发现/心跳过期（registry.json 持久化）。"""

    STALE_S = 60  # 心跳过期阈值（秒）

    def __init__(self, root: str):
        self.path = os.path.join(root, "registry.json")
        os.makedirs(root, exist_ok=True)
        self.nodes = {}
        if os.path.exists(self.path):
            try:
                self.nodes = json.load(open(self.path, encoding="utf-8"))
            except json.JSONDecodeError:
                self.nodes = {}

    def register(self, node_id: str, capabilities: list, roles: list | None = None):
        self.nodes[node_id] = {"capabilities": list(capabilities),
                               "roles": list(roles or []),
                               "last_seen": time.time()}
        self._save()

    def heartbeat(self, node_id: str):
        if node_id in self.nodes:
            self.nodes[node_id]["last_seen"] = time.time()
            self._save()

    def prune(self) -> list:
        dead = [n for n, v in self.nodes.items()
                if time.time() - v.get("last_seen", 0) > self.STALE_S]
        for n in dead:
            del self.nodes[n]
        if dead:
            self._save()
        return dead

    def by_capability(self, cap: str) -> list:
        return [n for n, v in self.nodes.items()
                if cap in v.get("capabilities", [])]

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.nodes, f, ensure_ascii=False, indent=1)


class RoleNegotiator:
    """职责协商：ROLE_OFFER → ROLE_REPLY(四态) → ROLE_CONFIRM 租约登记。

    租约 = {role → {node, expire_at}}；冲突（双节点同角色）→ 信任高者得；
    instance.vitals（维生系统）不可协商——终裁权在协议外（理论原文）。
    """

    def __init__(self, bus, self_id: str, trust: object, ttl_s: int = 300):
        self.bus = bus
        self.id = self_id
        self.trust = trust          # M3 TrustLedger（信任排序/冲突裁决）
        self.ttl_s = ttl_s
        self.leases: dict[str, dict] = {}   # role → {node, expire_at}
        self.log: list = []

    def offer(self, role: str, node: str) -> dict:
        if role not in ROLES:
            raise ProtocolError(f"不可协商角色: {role}（vitals 终裁权在协议外）")
        offer = make_msg("ROLE_OFFER", self.id, node, {"role": role, "ttl_s": self.ttl_s})
        if self.bus:                       # bus=None → 本地断言模式（只构造）
            self.bus.send(offer)
        self.log.append(offer)
        return offer

    def reply_accept(self, offer_msg, reason=""):
        if not self.bus:
            return
        self.bus.send(make_msg("ROLE_REPLY", self.id, offer_msg["from"],
                               {"verdict": "ACCEPT", "reason": reason,
                                "role": offer_msg["payload"]["role"]},
                               reply_to=offer_msg["id"]))

    def reply_reject(self, offer_msg, reason):
        if not self.bus:
            return
        self.bus.send(make_msg("ROLE_REPLY", self.id, offer_msg["from"],
                               {"verdict": "REJECT", "reason": reason,
                                "role": offer_msg["payload"]["role"]},
                               reply_to=offer_msg["id"]))

    def confirm(self, role: str, node: str) -> dict:
        lease = {"node": node,
                 "expire_at": time.time() + self.ttl_s,
                 "lease_id": f"L{uuid.uuid4().hex[:8]}"}
        self.leases[role] = lease
        c = make_msg("ROLE_CONFIRM", self.id, node,
                     {"role": role, "lease": lease}, reply_to=None)
        if self.bus:
            self.bus.send(c)
        self.log.append(c)
        return lease

    def resolve_conflict(self, role: str, cand_a: str, cand_b: str) -> str:
        """角色冲突：信任分高者得（M3 信任决定分工）。"""
        ta = self.trust.score(cand_a) if self.trust else 0.5
        tb = self.trust.score(cand_b) if self.trust else 0.5
        return cand_a if ta >= tb else cand_b

    def expire(self) -> list:
        now = time.time()
        expired = [r for r, l in self.leases.items() if l["expire_at"] < now]
        for r in expired:
            del self.leases[r]   # 到期失效（可重协商恢复，不删历史）
        return expired

    def holder(self, role: str) -> str | None:
        l = self.leases.get(role)
        return l["node"] if l and l["expire_at"] >= time.time() else None


if __name__ == "__main__":
    import sys, tempfile
    sys.stdout.reconfigure(encoding="utf-8")
    root = tempfile.mkdtemp(prefix="so_demo_")
    reg = Registry(root)
    reg.register("nodeA", ["校验", "编排"], roles=["verify"])
    reg.register("nodeB", ["求和", "世界模型"], roles=["reflect"])
    print("目录:", json.dumps(reg.nodes, ensure_ascii=False)[:120])
    print("按能力查:", reg.by_capability("求和"))
