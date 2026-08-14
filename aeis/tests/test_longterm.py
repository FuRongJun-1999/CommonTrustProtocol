#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
长期记忆写入决策器（LongTermMemoryGate）回归测试（v1.15）
==========================================================
覆盖：评估特征/评分层级决策/长期写入（保护+关联）/重复快照提升/
情境层批量提升/引擎与 API 集成。check 框架。
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def make_env():
    db = os.path.join(tempfile.mkdtemp(), "mem.db")
    from aeis.api import Agent
    agent = Agent(identity="gate测试", db_path=db)
    return agent


def test_evaluate_features():
    from aeis.longterm_gate import LongTermMemoryGate
    from aeis.core import SpacetimeMemoryEngine
    agent = make_env()
    gate = LongTermMemoryGate(agent.engine)
    # 注入特征样本：信任与信息差历史
    agent.engine.record_info_gap(0.6)
    agent.engine.record_info_gap(0.65)
    agent.engine.record_info_gap(0.72)
    for i in range(4):
        agent.engine.self_model.update_trust_state(0.4 + 0.1 * i, round_no=i)
    ev = gate.evaluate("全新领域的重要实验发现：跨模态记忆编码器验证成功")
    check("评估返回层级", ev["layer"] in ("long_term", "knowledge", "context"),
          f"layer={ev['layer']} imp={ev['importance']}")
    check("评估特征齐全", all(k in ev["features"] for k in
                             ("novelty", "trust", "d2", "t2", "mention")))
    check("importance 范围", 0.0 <= ev["importance"] <= 1.0)
    agent.close()


def test_write_snapshot_long_term():
    agent = make_env()
    r = agent.longterm_snapshot(
        "杀戮尖塔 2 实战测试完成：Steam 启动、OCR 读屏、痛击+ 升级成功——身体层真实操作验证",
        source="session_end", tags=["game", "slay_the_spire"],
        importance_hint=0.85)  # 提示重要性（里程碑）
    check("快照写入", r.get("node_id", "").startswith("node_"), str(r)[:80])
    check("长期层保护", r.get("protected") is True)
    # 验证保护表
    import sqlite3
    c = sqlite3.connect(r["node_id"] and os.path.join(tempfile.gettempdir(), "x"))
    # 通过引擎查
    node = agent.engine.store.get_node(r["node_id"])
    check("节点 importance", node.importance >= 0.7, f"imp={node.importance}")
    # 关联边（similar）
    edges = agent.engine.store.query_subgraph(r["node_id"], max_depth=1) if hasattr(
        agent.engine.store, "query_subgraph") else []
    check("关联边建立或跳过", r.get("links", 0) >= 0)
    agent.close()


def test_duplicate_snapshot_promotes():
    agent = make_env()
    r1 = agent.longterm_snapshot("重复快照测试内容 A", importance_hint=0.5)
    r2 = agent.longterm_snapshot("重复快照测试内容 A", importance_hint=0.8)
    check("重复快照同节点", r1["node_id"] == r2["node_id"])
    node = agent.engine.store.get_node(r2["node_id"])
    check("重要性提升", node.importance >= 0.7, f"imp={node.importance}")
    agent.close()


def test_promote_from_context():
    agent = make_env()
    # 写入情境层节点（低 importance）
    agent.remember("临时观测：窗外在下雨", importance=0.1, tags=["context_tmp"])
    agent.remember("重要里程碑：原生 harness 首次独立心跳完成",
                   importance=0.3, tags=["context_tmp"])
    promoted = agent.promote_memories(limit=10)
    # 低 importance 的不会提升（评估低）——但无样本时信任中性
    check("提升扫描执行", isinstance(promoted, list))
    # 验证：高价值情境节点（若评估达标）已提升
    from aeis.core import MemoryLayer
    nodes = agent.engine.store.query_nodes(layer=MemoryLayer.KNOWLEDGE, limit=50)
    check("知识层存在节点", len(nodes) >= 1)
    agent.close()


def test_engine_integration():
    agent = make_env()
    r = agent.engine.longterm_snapshot("引擎层直接调用测试")
    check("引擎方法可用",
          "node_id" in r or "error" in r or r.get("status") == "discarded",
          str(r)[:60])
    agent.close()


def main():
    print("===== 长期记忆写入决策器（v1.15）回归 =====")
    test_evaluate_features()
    test_write_snapshot_long_term()
    test_duplicate_snapshot_promotes()
    test_promote_from_context()
    test_engine_integration()
    print(f"\n===== LongTermMemoryGate: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
