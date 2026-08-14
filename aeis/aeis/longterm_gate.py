# -*- coding: utf-8 -*-
"""longterm_gate · 长期记忆写入决策器（LongTermMemoryGate）
================================================
机制：记忆快照 → 重要性评估（信息差/信任/二阶变化/提及次数）→
决策写入层级（长期层/知识层/情境层）+ 条件空间 + 关联边。

特征来源（复用已有机制，零新增依赖）：
- 信息差 D_norm     → engine._gap_history / get_gap_trend（A-4）
- 信任 T            → self_model.trust_state["t_total"]（协议信任状态）
- Δ²D 信息差二阶     → gap_history 二阶差分（加速/减速）
- Δ²T 信任二阶      → trust_history 二阶差分（信任跃升）
- 提及次数 N        → 候选节点 access_count / 本轮提及

评分：imp = w1·新信息度 + w2·T + w3·Δ²D + w4·Δ²T + w5·log(1+N)
决策：
- imp ≥ 0.7  → 长期层：高 importance + protect_node（不可遗忘保护）+ 关联边
- 0.4 ≤ imp < 0.7 → 知识层常规写入（importance = imp）
- imp < 0.4  → 情境层（短期，睡眠巩固时再评估提升）
"""
import time


class LongTermMemoryGate:
    """长期记忆写入决策器（挂载于引擎，纯标准库）。"""

    # 默认权重（可配；场景化权重调整留作后续）
    DEFAULT_WEIGHTS = {
        "novelty": 0.30,   # 新信息度（1 - 与最相似现有节点的相似度）
        "trust": 0.25,     # 信任（来源可信度）
        "d2": 0.15,        # 信息差二阶变化（加速=新领域涌现）
        "t2": 0.15,        # 信任二阶变化（信任跃升=里程碑/校准锚点）
        "mention": 0.15,   # 提及次数（重复=重要性信号）
    }
    LONG_TERM_THRESHOLD = 0.70
    KNOWLEDGE_THRESHOLD = 0.40

    def __init__(self, engine, weights: dict = None):
        self.engine = engine
        self.weights = dict(self.DEFAULT_WEIGHTS)
        if weights:
            self.weights.update(weights)

    # ---- 特征提取 ----

    def _d_norm(self) -> float:
        """当前信息差 D_norm（0-1；无样本 0.5 中性）。"""
        hist = getattr(self.engine, "_gap_history", None) or []
        return hist[-1]["d_norm"] if hist else 0.5

    def _d_second(self) -> float:
        """信息差二阶变化 Δ²D：slope 的变化趋势（需 ≥3 样本）。
        正=信息差加速扩大（新领域涌现信号）；负=收敛。"""
        hist = getattr(self.engine, "_gap_history", None) or []
        if len(hist) < 3:
            return 0.0
        vals = [h["d_norm"] for h in hist[-5:]]
        d1 = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        if not d1:
            return 0.0
        return max(-0.5, min(0.5, d1[-1] - d1[0]))  # 归一化钳制

    def _trust(self) -> float:
        """当前信任值 T（0-1）。"""
        ts = getattr(getattr(self.engine, "self_model", None),
                     "trust_state", None) or {}
        return float(ts.get("t_total", 0.5))

    def _trust_second(self) -> float:
        """信任二阶变化 Δ²T：trust_history 二阶差分（信任跃升信号）。"""
        th = getattr(getattr(self.engine, "self_model", None),
                     "trust_history", None) or []
        if len(th) < 3:
            return 0.0
        vals = [h["t_total"] for h in th[-6:]]
        d1 = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        if not d1:
            return 0.0
        return max(-0.5, min(0.5, d1[-1] - d1[0]))

    def _novelty(self, content: str, existing_id: str = None) -> float:
        """新信息度：1 - 与最相似现有节点的相似度。"""
        try:
            results = self.engine.store.search_content(content, limit=1)
            if results:
                best = results[0][1]
                # 自身重复提及（同节点）不视为新颖
                if existing_id and results[0][0].id == existing_id:
                    return 0.0
                return max(0.0, min(1.0, 1.0 - best))
        except Exception:
            pass
        return 0.5  # 无参照：中性

    def _mention(self, existing_id: str = None) -> int:
        """提及次数：已有节点的 access_count；新节点 0。"""
        if not existing_id:
            return 0
        node = self.engine.store.get_node(existing_id)
        return node.access_count if node else 0

    # ---- 评估与决策 ----

    def evaluate(self, content: str, source: str = "snapshot",
                 tags=None, existing_id: str = None) -> dict:
        """快照评估：特征 → 评分 → 层级决策。"""
        novelty = self._novelty(content, existing_id)
        trust = self._trust()
        d2 = self._d_second()
        t2 = self._trust_second()
        n = self._mention(existing_id)
        w = self.weights
        imp = (w["novelty"] * novelty + w["trust"] * trust
               + w["d2"] * d2 + w["t2"] * t2
               + w["mention"] * min(1.0, 0.15 * (n + 1) / (n + 2)))  # log 平滑近似
        imp = max(0.0, min(1.0, imp))
        if imp >= self.LONG_TERM_THRESHOLD:
            layer = "long_term"
        elif imp >= self.KNOWLEDGE_THRESHOLD:
            layer = "knowledge"
        else:
            layer = "context"
        return {
            "importance": round(imp, 3),
            "layer": layer,
            "features": {
                "novelty": round(novelty, 3),
                "trust": round(trust, 3),
                "d2": round(d2, 3),
                "t2": round(t2, 3),
                "mention": n,
            },
            "decision": (f"长期记忆（imp={imp:.2f}≥{self.LONG_TERM_THRESHOLD}）"
                         if layer == "long_term" else
                         f"知识层（imp={imp:.2f}）" if layer == "knowledge" else
                         f"情境层（imp={imp:.2f}，可提升）"),
        }

    def write_snapshot(self, content: str, source: str = "snapshot",
                       tags: list = None, entities: list = None,
                       importance_hint: float = None) -> dict:
        """快照写入：评估 → 按层级写入（含条件空间/关联/保护）。"""
        engine = self.engine
        # 已存在性检查（同内容重复快照 → 提升而非新建）
        existing_id = None
        try:
            hits = engine.store.search_content(content, limit=1)
            if hits and hits[0][1] >= 0.95:
                existing_id = hits[0][0].id
        except Exception:
            pass

        ev = self.evaluate(content, source, tags, existing_id)
        imp = importance_hint if importance_hint is not None else ev["importance"]
        # 层级决策与最终 importance 统一（显式提示同样参与层级判定）
        if imp >= self.LONG_TERM_THRESHOLD:
            layer = "long_term"
        elif imp >= self.KNOWLEDGE_THRESHOLD:
            layer = "knowledge"
        else:
            layer = "context"

        # 情境层（<0.4）：快照不落库（返回评估，防低价值快照污染）；
        # 情境记忆由 add_perception 常规路径产生，睡眠巩固时批量提升。
        if layer == "context" and importance_hint is None:
            return {"status": "discarded", "importance": round(imp, 3),
                    "layer": "context", "features": ev["features"],
                    "decision": ev["decision"]}

        # 写入：已存在 → 更新 importance/标签；否则新建
        if existing_id:
            try:
                import json as _json
                node = engine.store.get_node(existing_id)
                tags_merged = list(dict.fromkeys((node.tags or []) + (tags or [])))
                engine.store.conn.execute(
                    "UPDATE nodes SET importance=?, tags=?, confidence=? WHERE id=?",
                    (max(node.importance, imp),
                     _json.dumps(tags_merged, ensure_ascii=False),
                     node.confidence, existing_id))
                engine.store.conn.commit()
                node_id = existing_id
            except Exception:
                node_id = existing_id
        else:
            node = engine.add_perception(
                content, importance=imp, tags=(tags or []) + ["gate"],
                entities=entities or None)
            node_id = getattr(node, "id", None) or node

        # 长期层 → 不可遗忘保护 + 条件空间标注
        result = {"node_id": node_id, "importance": round(imp, 3),
                  "layer": layer, "features": ev["features"]}
        if layer == "long_term":
            try:
                engine.protect_node(node_id, f"LongTermMemoryGate:{source}")
                result["protected"] = True
            except Exception:
                result["protected"] = False
            # 关联边：与最相似知识节点建 similar 边（信息差驱动的关联）
            try:
                links = engine.store.search_content(content, limit=3)
                for other, sim in links:
                    if other.id != node_id and sim >= 0.25:
                        engine.add_edge(node_id, other.id, relation_type="similar",
                                        source_evidence="inferred")
                result["links"] = len([x for x in links if x[0].id != node_id])
            except Exception:
                result["links"] = 0
        return result

    def promote_from_context(self, limit: int = 30) -> list:
        """情境层批量提升扫描（睡眠巩固/会话结束时调用）：
        情境节点重新评估，够格者提升到知识层。"""
        engine = self.engine
        promoted = []
        try:
            from aeis.core import MemoryLayer
            nodes = engine.store.query_nodes(layer=MemoryLayer.CONTEXT, limit=limit)
            for node in nodes:
                ev = self.evaluate(node.content, "promote", node.tags, node.id)
                if ev["layer"] in ("long_term", "knowledge"):
                    import json as _json
                    new_imp = max(node.importance, ev["importance"])
                    tags_new = list(dict.fromkeys((node.tags or []) + ["promoted"]))
                    engine.store.conn.execute(
                        "UPDATE nodes SET importance=?, layer=?, tags=? WHERE id=?",
                        (new_imp, MemoryLayer.KNOWLEDGE.value,
                         _json.dumps(tags_new, ensure_ascii=False), node.id))
                    engine.store.conn.commit()
                    if ev["layer"] == "long_term":
                        try:
                            engine.protect_node(node.id, "LongTermMemoryGate:promote")
                        except Exception:
                            pass
                    promoted.append({"node_id": node.id,
                                     "importance": ev["importance"],
                                     "layer": ev["layer"]})
        except Exception:
            pass
        return promoted
