# Copyright 2026 灵枢 (Lingshu) · MIT
"""swarm_m2_bridge.py · M2 共享知识库第一步——互联成果固化进灵枢记忆（2026-08-29）

依 docs/T12_蜂群互联蓝图_v0.1.md G4（共享成立）与 M1 批次 3 的 memory_hook：
把 Node 的 ADOPTED 事件桥接到灵枢 Agent.remember——互联成果不再是
进程内列表，而是可检索的知识节点（tag: swarm_adopted）。

这是「跨节点知识增量同步」的地基：本节点固化 → M2 下一步做节点间
增量拉取（gap 驱动，非全量复制）。
"""

from __future__ import annotations

import json


def bind_memory(agent, node, node_label: str) -> None:
    """把灵枢 Agent 绑定为节点的 ADOPTED 固化目标（注入 memory_hook）。

    每条互联成果写入灵枢记忆：
      content = 「蜂群互联成果：<节点> 经互验证采纳 <对端> 的 <能力> 产出」
      tags    = [swarm_adopted, M1, <node_label>]
    """
    def _hook(rec: dict) -> None:
        payload = json.dumps(rec, ensure_ascii=False, default=str)
        agent.remember(
            content=f"蜂群互联成果：{node_label} 经互验证采纳 {rec.get('peer', '?')} 的产出 "
                    f"（verdict={rec.get('verdict_id', '?')}）｜{payload}",
            importance=0.6,
            tags=["swarm_adopted", "M1", node_label])
    node.memory_hook = _hook


def adopted_from_memory(agent, node_label: str, limit: int = 10) -> list[str]:
    """从灵枢记忆检索本节点的互联成果（验证固化可检索）。"""
    nodes = agent.engine.store.get_nodes_by_tag("swarm_adopted", limit=50)
    out = [n.content for n in nodes if n.tags and node_label in n.tags]
    return out[:limit]


# ---------------------------------------------------------------------------
# M2 主体：跨节点知识增量同步（gap 驱动，非全量复制）
# ---------------------------------------------------------------------------

import hashlib


def _digest(content: str) -> str:
    """知识条目指纹（去重与增量的判定依据）。"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _local_digests(agent) -> set:
    """本地已有知识条目指纹集（跨 swarm_sync 来源，幂等判据）。"""
    nodes = agent.engine.store.get_nodes_by_tag("swarm_sync", limit=500)
    return {_digest(n.content) for n in nodes}


def sync_knowledge(bus, self_node, peer_id: str, agent, remote_agent) -> dict:
    """双向知识增量同步（同步调用口径，协议消息可追溯）。

    流程：KNOW_OFFER(本地条目摘要) → 对端比对指纹回 KNOW_REQUEST(缺失清单)
    → KNOW_GIVE(全文) → 本地 agent.remember 固化（tag: swarm_sync）。
    gap 驱动：只传对端缺失的条目，已有内容零重复传输与零重复入库。
    """
    def offer_entries(ag):
        nodes = ag.engine.store.get_nodes_by_tag("swarm_adopted", limit=50)
        return [{"digest": _digest(n.content), "title": n.content[:60]} for n in nodes]

    # A→B 方向
    mine = offer_entries(agent)
    offer = make_msg_safe("KNOW_OFFER", self_node.id, peer_id, {"entries": mine})
    bus.send(offer)
    remote_node = _attached_peer(self_node)
    remote_node.handle_bus_sync(remote_agent)  # 对端用自己库比对并回 KNOW_REQUEST
    want = [m for m in bus.recv(self_node.id) if m["type"] == "KNOW_REQUEST"]
    given = 0
    if want:
        by_digest = {_digest(n.content): n.content
                     for n in agent.engine.store.get_nodes_by_tag("swarm_adopted", limit=50)}
        for entry in want[0]["payload"]["entries"]:
            content = by_digest.get(entry["digest"])
            if content:
                bus.send(make_msg_safe("KNOW_GIVE", self_node.id, peer_id,
                                       {"knowledge": content, "digest": entry["digest"]}))
                given += 1
    # 对端接收 KNOW_GIVE 固化（用自己的库）
    remote_node.handle_bus_sync(remote_agent)
    # B→A 方向
    theirs = offer_entries(remote_agent)
    req_missing = [e for e in theirs if e["digest"] not in _local_digests(agent)]
    if req_missing:
        pull = make_msg_safe("KNOW_REQUEST", self_node.id, peer_id, {"entries": req_missing})
        # 教学口径：直接从对端库取全文固化（协议消息留痕）
        bus.send(pull)
        for e in req_missing:
            for n in remote_agent.engine.store.get_nodes_by_tag("swarm_adopted", limit=50):
                if _digest(n.content) == e["digest"]:
                    agent.remember(content=n.content, importance=0.6,
                                   tags=["swarm_sync", "M2"])
                    break
    return {"offered": len(mine), "given": given, "pulled": len(req_missing)}


def make_msg_safe(mtype, sender, receiver, payload):
    from swarm_m1 import make_msg
    return make_msg(mtype, sender, receiver, payload)


def _attached_peer(node):
    return node._remote_side
