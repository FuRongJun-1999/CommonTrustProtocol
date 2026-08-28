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
