# -*- coding: utf-8 -*-
"""navigate.py · CSPRE 导航递归（《导航递归CSPRE_实现文档_v0.1》落地）

核心：条件空间导航递归——graph_retrieve 命中复合知识后，进入其内部
的条件路由继续导航（知识描述知识 = 条件路由图的子递归），直到原子知识
或深度上限（≤3，超出 = structural_blindspot，复用 core.py 递归约束模式）。

单源纪律：
- 复合/原子判定：state_attributes.knowledge_type 缺省 atomic（读时缺省，
  不物理写死 2846 条——避免无意义整图指纹扰动）
- 子路由索引复用 KCCS 注释索引（card_route），不新建体系
- 深度边界复用 core.py 递归约束模式（depth >= max_depth → structural_blindspot）
"""
from __future__ import annotations

import hashlib
import json


def get_knowledge_type(state_attributes) -> str:
    """复合/原子判定：读取时缺省 atomic。"""
    return state_attributes.get("knowledge_type", "atomic") \
        if isinstance(state_attributes, dict) else "atomic"


def get_sub_route(state_attributes) -> str:
    """复合节点的子路由条件空间词（仅 composite 有效）。"""
    return state_attributes.get("sub_route", "") \
        if isinstance(state_attributes, dict) else ""


def _canonical(obj) -> str:
    def norm(x):
        if isinstance(x, str):
            return x.strip()
        if isinstance(x, dict):
            return {k: norm(v) for k, v in sorted(x.items())}
        return x
    return json.dumps(norm(obj), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


def chain_fingerprint(chain: list) -> str:
    """导航链指纹（对接指纹化 L3：每次导航的可核对章）。"""
    payload = [{"depth": c.get("depth"), "condition_space": c.get("condition_space"),
                "rule": c.get("rule"), "node_id": c.get("node_id")}
               for c in chain]
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def refine_question(question: str, parent_sa: dict) -> str:
    """子问题条件收窄：拼入父节点子路由词，令子路由索引聚焦该条件空间
    （实现文档 §3.3——防子路由重新发散）。"""
    sub = get_sub_route(parent_sa)
    return f"{question} {sub}" if sub else question


def _load_state(dex, node_id):
    if not node_id:
        return {}
    store = getattr(dex, "store", None)
    if store is None:
        engine = getattr(dex, "engine", None)
        store = getattr(engine, "store", None)
    n = store.get_node(node_id) if store is not None else None
    return getattr(n, "state_attributes", {}) or {}


def _result(status: str, chain: list, **extra) -> dict:
    out = {"status": status,
           "navigation": "→".join(c["rule"] for c in chain),
           "chain": chain,
           "fingerprint": chain_fingerprint(chain),
           "depth_used": len(chain)}
    out.update(extra)
    return out


def navigate_retrieve(dex, question: str, *, max_depth: int = 3,
                      chain: list | None = None,
                      seen: set | None = None) -> dict:
    """条件空间导航递归主入口（CSPRE v0.1 · 实现文档 §3.2）。

    定位器分层：第 0 层 = graph_retrieve（四路融合）；
    第 ≥1 层 = card_route（KCCS 注释索引，子条件空间内收敛）。
    """
    from semantic_translate import graph_retrieve, card_route

    chain = list(chain or [])
    seen = set(seen or [])

    # 0. 深度边界（超出 = structural_blindspot）
    if len(chain) >= max_depth:
        return _result("structural_blindspot", chain,
                       note=f"递归深度已达上限 {max_depth}（3.12 运行约束）")

    # 1. 当前层定位
    if len(chain) == 0:
        hits = graph_retrieve(dex, question, limit=5) or []
        structured_rank = [h for h in hits]           # 已按融合分排序
        mode = "graph"
    else:
        raw = card_route(dex, question, limit=5) or []
        structured_rank = [h for h in raw if isinstance(h, dict)]
        mode = "kccs_index"
    if not structured_rank:
        return _result("no_route", chain,
                       reason="条件路由图无命中（诚实边界：未覆盖）",
                       mode=mode)

    top = structured_rank[0]
    nid = top.get("id")
    sa = _load_state(dex, nid)

    entry = {"depth": len(chain),
             "condition_space": top.get("domain_group") or top.get("domain") or "-",
             "rule": top.get("name") or "",
             "confidence": top.get("score"),
             "node_id": nid,
             "knowledge_type": get_knowledge_type(sa)}
    chain.append(entry)

    # 2. 循环防护（同一 条件空间|规则 只走一次）
    rule_key = f'{entry["condition_space"]}|{entry["rule"]}'
    if rule_key in seen:
        return _result("structural_blindspot", chain,
                       note="循环导航检测：相同规则重复出现")
    seen.add(rule_key)

    # 3. 原子 → 终答；复合 → 收窄后进入子路由
    if entry["knowledge_type"] != "composite":
        return _result("resolved", chain,
                       answer="",
                       direct_answer=top.get("direct_answer") or "",
                       verdict="ACCEPT" if top.get("_card_hit") else "DEFER")

    sub_q = refine_question(question, sa)
    return navigate_retrieve(dex, sub_q, max_depth=max_depth,
                             chain=chain, seen=seen)


__all__ = ["get_knowledge_type", "get_sub_route", "refine_question",
           "navigate_retrieve", "chain_fingerprint"]
