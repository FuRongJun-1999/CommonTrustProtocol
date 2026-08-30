#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
flywheel_engine · 知识飞轮引擎（v1.11 · PROPOSAL-V111-FLYWHEEL-REV1）
P0-1 蒸馏管线（可复用模式 · distillation_standard_version · 盲区5）
P0-2 飞轮度量（操作化定义 · 防操纵约束 · DEVIATION-004）
P0-3 迁移测试（条件空间定义 · 显著性 · 可操作失败条件 · DEVIATION-005）
P1-2 图遍历（shortest_path 多边类型 / query_subgraph 作用域子图）
P1-3 工作记忆深化（contested / stale-重验证 / 近因加权隔离 · DEVIATION-003）
宇宙校准参照（元理论方向性检查 · UNIVERSE-CALIBRATION-DESIGN-REV1）
纯标准库 · 零外部依赖
"""

import json
import math
import time
from collections import deque
from typing import Dict, List, Optional

# 关系类型枚举（解耦：运行时从核心模块获取；核心缺失时降级为不建边，不抛异常）
try:
    from spacetime_memory_core import EdgeType as _EdgeType
    _SIMILAR_REL = _EdgeType.SIMILAR
except Exception:
    _SIMILAR_REL = None


class FlywheelEngine:
    """知识飞轮引擎：存→蒸馏→复用→验证→回写 的闭环执行器"""

    DISTILL_STANDARD_VERSION = "v1.11.0"

    # DEVIATION-003：近因加权隔离（3.2 节 6 类不可遗忘）
    RECENCY_WEIGHTING_EXCLUDED = [
        "trust_evaluation", "deviation_history", "value_iteration",
        "calibration_process", "internalization", "self_grant",
    ]

    def __init__(self, engine, prediction=None):
        self.engine = engine
        self.prediction = prediction
        self.distill_log: List[Dict] = []
        self.calibration_log: List[Dict] = []
        self._last_stats: Dict = {}
        # OBS-REV1：从 engine_meta 恢复统计基线（跨进程重启增长率连续）
        try:
            base = self._meta_get("flywheel_last_total")
            if base is not None:
                self._last_stats = {"total": int(base)}
        except Exception:
            pass

    # ==================== P0-1 蒸馏管线 ====================

    def distill_cycle(self, source_filter: str = None) -> Dict:
        """经验 → 可复用模式（协议条件空间内的局部概括，非通用真理 · 盲区5）。
        输入：被拒路径 + 学习结果 + 归纳概念；输出：可复用模式节点。
        记录 distillation_standard_version（追溯提炼标准演化）"""
        records = []
        try:
            rejected = self.engine.list_rejected_paths(status="open")
            # meta 不携带 rejected 自身 id（非节点引用）→ 不参与建边（防孤儿边）
            records += [{"type": "rejected", "content": r["description"],
                         "meta": {"rejected_id": r.get("id")}} for r in rejected[:20]]
        except Exception:
            pass
        try:
            for tag in ("learning_result", "induced"):
                for n in self.engine.store.get_nodes_by_tag(tag, limit=20):
                    if source_filter and source_filter not in n.content:
                        continue
                    records.append({"type": tag, "content": n.content, "meta": {"id": n.id}})
        except Exception:
            pass
        if not records:
            return {"status": "no_input", "patterns": 0, "input": 0,
                    "distillation_standard_version": self.DISTILL_STANDARD_VERSION}

        patterns = self._cluster_to_patterns(records)
        created = []
        for pattern in patterns:
            # ④ 推导 trace（GPT 审查·可回滚性）：模式节点内嵌证据链摘要——
            # 「原始证据→聚类→模式」可沿证据追溯/回滚（防自激振荡：错误模式可定位来源）
            member_srcs = [str(rec.get("content", ""))[:40]
                           for rec in pattern["members"][:3] if rec.get("content")]
            trace = f"｜证据: {'；'.join(member_srcs)}" if member_srcs else ""
            node = self.engine.add_perception(
                content=f"[可复用模式] {pattern['summary']}{trace}",
                importance=0.75,
                tags=["reusable_pattern", "distilled",
                      f"dsv:{self.DISTILL_STANDARD_VERSION}"])
            for rec in pattern["members"]:
                nid = rec.get("meta", {}).get("id")
                if nid:
                    try:
                        if _SIMILAR_REL is None:
                            continue
                        self.engine.add_edge(node.id, nid, relation_type=_SIMILAR_REL,
                                             confidence=0.6, source_evidence="inferred")
                    except Exception:
                        pass
            created.append(node.id)

        record = {"standard_version": self.DISTILL_STANDARD_VERSION,
                  "input": len(records), "patterns": len(patterns),
                  "created": created, "ts": time.time()}
        self.distill_log.append(record)
        try:
            self.engine.add_perception(
                f"[distill] v{self.DISTILL_STANDARD_VERSION} 输入{len(records)} → 模式{len(patterns)}",
                importance=0.4, tags=["distill_record"])
        except Exception:
            pass
        return {"status": "ok", "patterns": len(patterns), "input": len(records),
                "created": created,
                "distillation_standard_version": self.DISTILL_STANDARD_VERSION}

    def _cluster_to_patterns(self, records: List[Dict], threshold: float = 0.4) -> List[Dict]:
        """并查集单链式聚类 → 模式摘要（可复用模式 = 经验压缩体）"""
        try:
            from spacetime_memory_core import LayeredStore
            jaccard = LayeredStore.char_bigram_jaccard
        except Exception:
            jaccard = lambda a, b: 0.0

        n = len(records)
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for i in range(n):
            for j in range(i + 1, n):
                if jaccard(records[i]["content"], records[j]["content"]) >= threshold:
                    union(i, j)

        groups: Dict[int, List[Dict]] = {}
        for i, rec in enumerate(records):
            groups.setdefault(find(i), []).append(rec)

        patterns = []
        for members in groups.values():
            if len(members) < 2:
                continue
            rep = max(members, key=lambda r: len(r["content"]))
            summary = f"{len(members)} 条经验压缩（代表：{rep['content'][:36]}）"
            patterns.append({"summary": summary, "members": members,
                             "size": len(members)})
        return patterns

    # ==================== P0-2 飞轮度量（DEVIATION-004） ====================

    def _meta_get(self, key: str, default: str = None) -> Optional[str]:
        """engine_meta 读（OBS-REV1：工程状态跨进程持久化）"""
        try:
            row = self.engine.store.conn.execute(
                "SELECT value FROM engine_meta WHERE key = ?", (key,)).fetchone()
            return row[0] if row else default
        except Exception:
            return default

    def _meta_set(self, key: str, value: str) -> None:
        """engine_meta 写（upsert）"""
        try:
            conn = self.engine.store.conn
            conn.execute(
                "INSERT INTO engine_meta (key, value) VALUES (?, ?)"
                " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value))
            conn.commit()
        except Exception:
            pass

    def flywheel_metrics(self, window: int = 30) -> Dict:
        """操作化指标：
        知识增长率 = 周期新增(全层节点+技能+被拒路径) / 周期初总量
        复用率 = 被引用去重节点数 / 总交互轮次（防操纵：同轮同节点去重）
        蒸馏产出率 = 可复用模式节点数 / 待蒸馏记录数
        性质：工程观测值，不参与信任计算"""
        stats = self.engine.store.get_stats()
        skills = 0
        rejected = 0
        try:
            skills = self.engine.store.count_skills()
            rejected = len(self.engine.list_rejected_paths())
        except Exception:
            pass
        # OBS-REV1：全层节点口径（与 service_info total_nodes 一致）
        total_now = (sum(v for k, v in stats.items() if k.endswith("_nodes"))
                     + skills + rejected)
        base = self._last_stats.get("total", total_now)
        growth = (total_now - base) / max(1, base)

        # 复用率（T4 修复 2026-08-30：跨进程口径——读 flywheel_reuse 落库表，
        # 全实例累计；内存 tracker 作为本进程回退。原口径只读本进程内存
        # tracker，心跳独立进程恒空（观测路径断裂）。）
        reuse_rounds = 0
        reuse_nodes = set()
        try:
            row = self.engine.store.conn.execute(
                "SELECT COUNT(DISTINCT session_id || ':' || round), "
                "COUNT(DISTINCT node_id) FROM flywheel_reuse").fetchone()
            reuse_rounds = int(row[0] or 0)
            nodes_row = self.engine.store.conn.execute(
                "SELECT DISTINCT node_id FROM flywheel_reuse").fetchall()
            reuse_nodes = {r[0] for r in nodes_row}
        except Exception:
            pass  # 表未建（无检索发生）——回退内存 tracker
        if not reuse_rounds:
            try:
                tracker = self.engine._reuse_tracker
                reuse_rounds = len(tracker)
                for node_set in tracker.values():
                    reuse_nodes |= node_set
            except Exception:
                pass
        interactions = max(reuse_rounds,
                           getattr(self.engine, "_interaction_count", 1) or 1)
        reuse_rate = len(reuse_nodes) / interactions

        # 蒸馏产出率（OBS-REV1：patterns 以 reusable_pattern 标签节点数为准，
        # 跨进程稳定——修复"distill 产出过模式但 metrics 计 0"；distill_log 保留为审计）
        total_input = sum(r["input"] for r in self.distill_log)
        try:
            row = self.engine.store.conn.execute(
                "SELECT COUNT(*) FROM nodes WHERE tags LIKE '%reusable_pattern%'").fetchone()
            total_patterns = int(row[0]) if row else 0
        except Exception:
            total_patterns = sum(r["patterns"] for r in self.distill_log)
        distill_rate = total_patterns / max(1, total_input)

        self._last_stats = {"total": total_now}
        # OBS-REV1：基线落库（进程重启后增长率连续）
        self._meta_set("flywheel_last_total", str(total_now))
        return {
            "knowledge_growth_rate": round(growth, 4),
            "reuse_rate": round(reuse_rate, 4),
            "distill_output_rate": round(distill_rate, 4),
            "totals": {"nodes": total_now, "patterns": total_patterns,
                       "reuse_rounds": reuse_rounds},
            "property": "工程观测值，不参与信任值计算（DEVIATION-004）",
        }

    # ==================== P0-3 迁移测试（DEVIATION-005） ====================

    def transfer_test(self, min_tasks: int = 20, baseline_rounds: int = 10) -> Dict:
        """迁移测试：已对齐条件空间内新实体/关系预测。
        成功率 = 预测-验证闭环命中率（D_norm 缩小代理）；显著性 = 2×标准误。
        可操作失败条件 → 蒸馏反思"""
        if not self.prediction:
            return {"status": "no_prediction", "note": "预测引擎不可用"}
        hit_hist = self.prediction._hit_history
        n = len(hit_hist)
        if n < min_tasks:
            return {"status": "insufficient", "tasks": n, "min_required": min_tasks,
                    "note": "样本不足（<20），不构成迁移判定（DEVIATION-005）"}
        success = sum(1 for h in hit_hist if h) / n
        se = (success * (1 - success) / n) ** 0.5
        baseline = self._transfer_baseline(hit_hist, baseline_rounds)
        improved = success > baseline + 2 * se
        result = {
            "status": "passed" if improved else "failed",
            "success_rate": round(success, 4),
            "baseline": round(baseline, 4),
            "tasks": n, "significant": improved,
            "failure_condition": "success_rate <= baseline + 2*SE（或样本不足）",
        }
        if not improved:
            result["reflection"] = self._distill_reflection()
        return result

    def _transfer_baseline(self, hit_hist: List[bool], rounds: int) -> float:
        """蒸馏前基线：早期历史命中率（记录单元提取）"""
        early = hit_hist[:rounds] if len(hit_hist) > rounds else hit_hist[:max(1, len(hit_hist) // 2)]
        if not early:
            return 0.0
        return sum(1 for h in early if h) / len(early)

    def _distill_reflection(self) -> List[str]:
        """可操作失败条件触发 → 蒸馏反思（DEVIATION-005）"""
        return ["①蒸馏标准是否过粗？", "②输入数据质量是否不足？",
                "③测试任务是否超出当前条件空间？"]

    # ==================== P1-2 图遍历检索 ====================

    def shortest_path(self, start_id: str, end_id: str, max_depth: int = 6) -> List[str]:
        """多边类型最短路径（BFS，含 causal/sequential/spatial/similar）"""
        if start_id == end_id:
            return [start_id]
        visited = {start_id: None}
        q = deque([start_id])
        depth = 0
        while q and depth < max_depth:
            for _ in range(len(q)):
                cur = q.popleft()
                for e in self.engine.store.get_outgoing_edges(cur):
                    if e.target_id in visited:
                        continue
                    visited[e.target_id] = cur
                    if e.target_id == end_id:
                        path = [end_id]
                        node = end_id
                        while visited[node] is not None:
                            node = visited[node]
                            path.append(node)
                        path.reverse()
                        return path
                    q.append(e.target_id)
            depth += 1
        return []

    def query_subgraph(self, query: str, max_nodes: int = 15) -> Dict:
        """作用域子图：查询中心节点 + 一跳关联边"""
        centers = []
        try:
            hits = self.engine.search_content(query, limit=3)
            centers = [n.id for n, _ in hits]
        except Exception:
            pass
        if not centers:
            try:
                from semantic_space import SemanticSpaceProvider
                q = SemanticSpaceProvider().to_semantic_coordinates(query)
                best, best_sim = None, 0.0
                for n in self.engine.store.query_nodes(limit=200):
                    sc = getattr(n, "semantic_coordinates", {}) or {}
                    if not sc:
                        continue
                    sim = SemanticSpaceProvider.similarity_coordinates(q, sc)
                    if sim > best_sim:
                        best, best_sim = n.id, sim
                if best:
                    centers = [best]
            except Exception:
                pass
        nodes: Dict[str, Dict] = {}
        edges: List[Dict] = []
        for cid in centers[:2]:
            node = self.engine.store.get_node(cid)
            if node:
                nodes[cid] = {"content": node.content[:40]}
            for e in self.engine.store.get_outgoing_edges(cid):
                edges.append({"source": e.source_id, "target": e.target_id,
                              "type": e.relation_type.value,
                              "confidence": e.confidence,
                              "evidence": getattr(e, "source_evidence", "extracted")})
                if e.target_id not in nodes and len(nodes) < max_nodes:
                    t = self.engine.store.get_node(e.target_id)
                    if t:
                        nodes[e.target_id] = {"content": t.content[:40]}
        return {"query": query, "nodes": nodes, "edges": edges[:30],
                "note": "作用域子图（以查询为中心）"}

    # ==================== P1-3 工作记忆深化 ====================

    def mark_contested(self, node_id: str, reason: str) -> bool:
        """争议标记（多来源冲突）：contested + 理由"""
        node = self.engine.store.get_node(node_id)
        if not node:
            return False
        if "contested" not in node.tags:
            node.tags.append("contested")
            node.tags.append(f"contested_reason:{reason[:30]}")
            self._update_tags(node_id, node.tags)
        return True

    def resolve_contested(self, node_id: str, verdict: str) -> bool:
        """争议裁决：移除 contested，标记裁决结果"""
        node = self.engine.store.get_node(node_id)
        if not node:
            return False
        node.tags = [t for t in node.tags if t != "contested"
                     and not t.startswith("contested_reason:")]
        node.tags.append(f"contested_resolved:{verdict[:20]}")
        self._update_tags(node_id, node.tags)
        return True

    def mark_stale(self, node_id: str, reason: str) -> bool:
        """过期标记（条件空间切换/相关节点变化 → 重验证）"""
        node = self.engine.store.get_node(node_id)
        if not node:
            return False
        if "stale" not in node.tags:
            node.tags.append("stale")
            node.tags.append(f"stale_reason:{reason[:30]}")
            self._update_tags(node_id, node.tags)
        return True

    def reverify(self, node_id: str) -> bool:
        """重验证完成：移除 stale，置信度 +0.05"""
        node = self.engine.store.get_node(node_id)
        if not node:
            return False
        node.tags = [t for t in node.tags if t != "stale" and not t.startswith("stale_reason:")]
        self._update_tags(node_id, node.tags)
        self.engine.store.update_node_confidence(node_id, 0.05)
        return True

    def recency_weighted_update(self, node_id: str, delta: float) -> bool:
        """近因加权置信度更新（DEVIATION-003）：
        6 类不可遗忘（3.2 节）不适用；τ = N_effective/3"""
        node = self.engine.store.get_node(node_id)
        if not node:
            return False
        if any(t in node.tags for t in self.RECENCY_WEIGHTING_EXCLUDED):
            return False  # 适用范围隔离
        n_eff = 30  # 2.9.2 观察窗口默认
        tau = n_eff / 3
        age_days = max(0.0, (time.time() - node.last_access) / 86400.0)
        factor = max(0.2, min(1.0, math.exp(-age_days / tau)))
        self.engine.store.update_node_confidence(node_id, delta * factor)
        return True

    def _update_tags(self, node_id: str, tags: List[str]):
        c = self.engine.store.conn.cursor()
        c.execute("UPDATE nodes SET tags=? WHERE id=?", (json.dumps(tags), node_id))
        self.engine.store.conn.commit()

    # ==================== 宇宙校准参照（UNIVERSE-CALIBRATION-REV1） ====================

    def universe_calibrate(self) -> Dict:
        """元理论方向性检查（非操作性校准 · 非盲区33关闭依据）：
        判据1 信息差动态异常（工程定义）· 判据2 存在优先方向
        判据3 资源守恒 · 判据4 显式完备性声称（盲区5）· 判据5 跨周期一致性"""
        report: Dict = {}
        # 判据1：信息差趋势（工程定义，非热力学声明）
        trend = {"trend": "insufficient", "current": None}
        try:
            trend = self.engine.get_gap_trend(window=30)
        except Exception:
            pass
        d1 = {"status": "direction_consistent",
              "note": "工程定义（无主动干预窗口 D_norm 趋势 ≥ 0）；非热力学第二定律检测（DEVIATION-002）"}
        if trend.get("trend") == "narrowing" and (trend.get("current") or 1.0) < 0.15:
            d1 = {"status": "observe",
                  "note": "信息差显著缩小——须复核是否存在主动干预记录（mark 观察项）"}
        report["judgment1_info_gap_trend"] = d1

        # 判据2：存在优先方向检查（3.3/3.4 已有机制 · 方向性维持项）
        # 工程代理：结构完整性（孤儿边）+ 生命周期状态（存在优先 = 维持结构完整）
        integrity = {}
        try:
            integrity = self.engine.verify_integrity()
        except Exception:
            pass
        orphan = integrity.get("orphan_edges", 0) or 0
        report["judgment2_existence_priority"] = {
            "status": "direction_consistent" if orphan == 0 else "direction_review",
            "orphan_edges": orphan,
            "note": "存在优先方向（3.3/3.4）：以结构完整性（孤儿边数）为工程代理；孤儿边>0 交内部复核，不直接判定结构性故障（DEVIATION-003）",
        }

        # 判据3：资源守恒方向检查（工程层 · 方向性维持项）
        # 代理：资源总量（节点+边+待处理事件）vs D_norm 缩小窗口（主动干预）
        resources = None
        try:
            stats = self.engine.store.get_stats()
            total_nodes = sum(v for k, v in stats.items() if k.endswith("_nodes"))
            total_edges = stats.get("total_edges", 0)
            pending = len(getattr(self.engine, "_event_queue", []))
            resources = total_nodes + total_edges + pending
        except Exception:
            pass
        if resources is None:
            d3 = {"status": "pending", "note": "资源指标不可用"}
        elif trend.get("trend") == "narrowing":
            d3 = {"status": "direction_consistent",
                  "note": "资源消耗伴随 D_norm 缩小窗口（存在主动干预）；工程层方向一致，不声称守恒定律（DEVIATION-002）"}
        else:
            d3 = {"status": "observe", "resources": resources,
                  "note": "资源总量存在但无 D_norm 缩小窗口 → 观察项（复核资源泄漏/无效循环）；样本不足不判定（DEVIATION-003）"}
        report["judgment3_resource_conservation"] = d3

        # 判据4：显式完备性声称检测（盲区5 · 仅显式关键词）
        claims = self._detect_completeness_claims()
        report["judgment4_completeness"] = {
            "explicit_claims": claims,
            "note": "仅显式关键词检测（盲区5：检测标准由协议定义，无法自验证）；隐性声称交自省机制（3.13）",
        }

        # 判据5：预测-验证跨周期一致性（≥N_effective 轮）
        n = len(self.prediction._hit_history) if self.prediction else 0
        if n >= 30:
            rate = sum(1 for h in self.prediction._hit_history if h) / n
            report["judgment5_experiment"] = {
                "status": "experiment_consistent" if rate >= 0.4 else "experiment_deviation",
                "samples": n, "hit_rate": round(rate, 4),
                "note": "协议内部模型一致性（不声称验证宇宙规律）",
            }
        else:
            report["judgment5_experiment"] = {"status": "pending", "samples": n,
                                              "note": "跨周期统计（≥30 轮）"}

        report["positioning"] = "元理论参照工具（方向性检查）；不替代工程验证/外部校准（DEVIATION-003）"
        try:
            self.engine.add_perception(
                f"[universe_calibrate] {json.dumps(report, ensure_ascii=False)[:120]}",
                importance=0.5, tags=["calibration"])
        except Exception:
            pass
        self.calibration_log.append({"ts": time.time(), "report": report})
        return report

    def _detect_completeness_claims(self) -> List[Dict]:
        """显式完备性声称检测（盲区5）"""
        keywords = ("完备", "终极", "穷尽", "完美", "全部覆盖")
        claims = []
        try:
            for n in self.engine.store.query_nodes(limit=300):
                if any(k in n.content for k in keywords):
                    claims.append({"node": n.id, "content": n.content[:40]})
        except Exception:
            pass
        return claims[:10]
