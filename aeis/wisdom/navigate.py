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

    # 1. 当前层定位：KCCS 注释索引（card_route）是纯条件核对层——
    #    实测它对「婆媳矛盾」命中复合根 raw=7 第一名，而 graph_retrieve
    #    四路融合会引入计算机卡 bigram 噪声（地基审计实证）。故各层统一
    #    用 card_route；空时才回退 graph_retrieve（诚实边界保底）。
    structured_rank = []
    mode = "kccs_index"
    raw = card_route(dex, question, limit=10) or []
    structured_rank = [h for h in raw if isinstance(h, dict)]
    if not structured_rank:
        hits = graph_retrieve(dex, question, limit=5) or []
        structured_rank = list(hits)
        mode = "graph_fallback"
    if not structured_rank:
        return _result("no_route", chain,
                       reason="条件路由图无命中（诚实边界：未覆盖）",
                       mode=mode)

    # 复合优先 + 已访问过滤（地图式收敛）：
    #   同层命中里若有未访问的 composite 节点 → 优先进入其子条件空间
    #   （先进城市再找街道）；否则取未访问的最高分 atomic 直答。
    #   已访问的规则跳过——防止同一入口反复入栈（循环防护）。
    entry = None
    atomic_fallback = None
    for h in structured_rank:
        nid = h.get("id")
        sa_h = _load_state(dex, nid)
        rule_key = f'{h.get("domain_group") or h.get("domain") or "-"}|{h.get("name") or ""}'
        if rule_key in seen:
            continue
        sa_h = dict(sa_h)
        sa_h.setdefault("sub_route", "")
        ktype = get_knowledge_type(sa_h)
        cand = {"depth": len(chain),
                "condition_space": h.get("domain_group") or h.get("domain") or "-",
                "rule": h.get("name") or "",
                "confidence": h.get("score"),
                "node_id": nid,
                "knowledge_type": ktype,
                "_sa": sa_h}
        if ktype == "composite":
            entry = cand
            break
        if atomic_fallback is None:
            atomic_fallback = cand
    if entry is None:
        entry = atomic_fallback
    if entry is None:
        return _result("structural_blindspot", chain,
                       note="全部候选均已导航过（循环耗尽）")
    chain.append(entry)
    seen.add(f'{entry["condition_space"]}|{entry["rule"]}')
    sa = entry["_sa"]

    # 3. 原子 → 终答；复合 → 收窄后进入子路由
    if entry["knowledge_type"] != "composite":
        return _result("resolved", chain,
                       answer="",
                       direct_answer=sa.get("comment", {}).get("执行", "")
                       if isinstance(sa.get("comment"), dict) else "",
                       verdict="ACCEPT")

    # composite：条件收窄（refine_question 用 entry 的 sub_route）
    sub_q = refine_question(question, sa)
    return navigate_retrieve(dex, sub_q, max_depth=max_depth,
                             chain=chain, seen=seen)


__all__ = ["get_knowledge_type", "get_sub_route", "refine_question",
           "navigate_retrieve", "chain_fingerprint"]
