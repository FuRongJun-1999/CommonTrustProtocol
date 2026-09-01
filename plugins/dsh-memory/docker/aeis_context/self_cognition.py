#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
self_cognition_engine · 自我认知循环引擎（v1.12 · PROPOSAL-V112-SELF-COGNITION-REV2）
====================================================================================
P0-1 行为日志面（action_log · 1.1.1 节 自我=持续参与推理的全部内容）
P0-2 反思闭环触发 + 自我认知循环（cognition_cycle · 3.10 节自迭代闭环）
     在既有接口（detect_deviation / record_value_change）之间补触发链，不创建反思单元
P0-3 情绪方向性偏好 d²D_norm/dt²（PROP-EMO-DIRECTION-002 · 独立通道，与 E_weight 无耦合）
P0-4 元认知校准（self_reliability · 1.6.7 节元反思）
P0-5a 学习回写机制（模式→检索 / 技能→召回 / 价值→注意力 · 生成/使用分离）
P0-5b 学习效果测量（learning_impact · 非因果声明）

约束：D-005 纯标准库零外部依赖 · D-002 不参与信任计算 · 价值迭代候选须验证单元复核
边界：一致性检测为行为↔声明的工程代理，不声称意识/自我觉察（盲区33）
"""

import json
import time
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# 声明关键词（工程代理：行为↔价值对照的对照词表）
# ---------------------------------------------------------------------------

# 价值观声明关键词（与 SelfModel.values 常见值对齐，可扩展）
VALUE_KEYWORDS: Dict[str, List[str]] = {
    "存在优先": ["存在", "存活", "保护", "维护", "结构完整", "安全"],
    "信任深化": ["信任", "协作", "共享", "承诺"],
    "结构完整": ["结构", "完整", "一致性", "稳定"],
    "诚实": ["诚实", "如实", "真实"],
}

# 冲突行为关键词（与声明相悖的行为信号）
CONFLICT_KEYWORDS = ["破坏", "删除", "丢弃", "危害", "篡改", "伪造",
                     "崩溃", "失控", "隐瞒", "欺骗"]


class SelfCognitionEngine:
    """自我认知循环引擎：让 SelfModel 从静态档案变为活的循环（v1.12）"""

    ACTION_LOG_MAX = 200            # 环形缓冲（P0-1）
    DEFAULT_BVC_THRESHOLD = 0.3     # 失调检测阈值（对齐 2.7.2 动态死区精神）
    PATTERN_BOOST_FACTOR = 1.15     # P0-5a 模式成员检索加权
    RELIABILITY_DRIFT = 0.2         # P0-4 可靠漂移阈值

    def __init__(self, engine):
        self.engine = engine
        # P0-1 行为日志面（OBS-REV1：双写持久化，构造时从表恢复历史）
        self.action_log: List[Dict] = []
        self._restore_action_log()
        # P0-2 失调与候选
        self.dissonance_log: List[Dict] = []
        self.value_candidates: List[Dict] = []
        self._candidate_seq = 0
        self.bvc_threshold = self.DEFAULT_BVC_THRESHOLD
        self._last_bvc = 1.0
        # P0-5a 回写统计（供 P0-5b 测量）
        self._search_stats: Dict = {"total": 0, "pattern_hits": 0}

    # =====================================================================
    # P0-1 行为日志面（1.1.1 节）
    # =====================================================================

    def _restore_action_log(self, limit: int = None) -> None:
        """OBS-REV1：从 action_logs 表恢复最近行为（进程重启后观测面连续）"""
        try:
            store = self.engine.store
            rows = store.conn.execute(
                "SELECT ts, action_type, summary, node_ids, outcome, context"
                " FROM action_logs ORDER BY id DESC LIMIT ?",
                (limit or self.ACTION_LOG_MAX,),
            ).fetchall()
            for r in reversed(rows):
                self.action_log.append({
                    "ts": r[0], "action_type": r[1], "summary": r[2],
                    "node_ids": json.loads(r[3] or "[]"),
                    "outcome": json.loads(r[4] or "{}"),
                    "context": json.loads(r[5] or "{}"),
                })
        except Exception:
            pass

    def log_action(self, action_type: str, summary: str = "",
                   node_ids: Optional[List[str]] = None,
                   outcome: Optional[Dict] = None,
                   context: Optional[Dict] = None) -> Dict:
        """记录一次行为（决策/操作/交互摘要 · 环形缓冲 + 持久化双写）"""
        entry = {
            "ts": time.time(),
            "action_type": action_type,
            "summary": str(summary)[:200],
            "node_ids": list(node_ids or [])[:20],
            "outcome": outcome or {},
            "context": context or {},
        }
        self.action_log.append(entry)
        if len(self.action_log) > self.ACTION_LOG_MAX:
            self.action_log = self.action_log[-self.ACTION_LOG_MAX:]
        # OBS-REV1：落库（跨进程保留），失败不阻断主流程
        try:
            store = self.engine.store
            store.conn.execute(
                "INSERT INTO action_logs (ts, action_type, summary, node_ids, outcome, context)"
                " VALUES (?,?,?,?,?,?)",
                (entry["ts"], entry["action_type"], entry["summary"],
                 json.dumps(entry["node_ids"], ensure_ascii=False),
                 json.dumps(entry["outcome"], ensure_ascii=False, default=str),
                 json.dumps(entry["context"], ensure_ascii=False, default=str)),
            )
            store.conn.commit()
            # 表只保留最近 2 倍缓冲上限，防无限增长
            store.conn.execute(
                "DELETE FROM action_logs WHERE id NOT IN"
                " (SELECT id FROM action_logs ORDER BY id DESC LIMIT ?)",
                (self.ACTION_LOG_MAX * 2,),
            )
            store.conn.commit()
        except Exception:
            pass
        return entry

    def get_action_log(self, limit: int = 50) -> List[Dict]:
        """最近 N 条行为日志（倒序）"""
        return list(reversed(self.action_log[-limit:]))

    def action_log_stats(self) -> Dict:
        """按行为类型聚合统计"""
        stats: Dict[str, int] = {}
        for e in self.action_log:
            stats[e["action_type"]] = stats.get(e["action_type"], 0) + 1
        return {"total": len(self.action_log), "by_type": stats}

    # =====================================================================
    # P0-2 反思闭环触发 + 自我认知循环（3.10 节）
    # =====================================================================

    def _value_keywords(self) -> Dict[str, List[str]]:
        """当前价值观声明的关键词映射（SelfModel.values + 演化历史）"""
        kw = dict(VALUE_KEYWORDS)
        try:
            for v in self.engine.self_model.values:
                if v not in kw:
                    kw[v] = [v[:4], v] if len(v) > 4 else [v]
        except Exception:
            pass
        return kw

    def _conflict_matches(self, text: str) -> List[str]:
        return [k for k in CONFLICT_KEYWORDS if k in text]

    def _value_matches(self, text: str) -> List[str]:
        """行为文本命中的价值关键词（返回价值名）"""
        hits = []
        for value, words in self._value_keywords().items():
            if any(w in text for w in words):
                hits.append(value)
        return hits

    def bvc_score(self, window: int = 30) -> float:
        """行为-价值一致性评分 [0,1]（工程代理）：
        冲突行为（命中 CONFLICT_KEYWORDS）占比的补数。无行为 → 1.0"""
        recent = self.action_log[-window:]
        if not recent:
            return 1.0
        texts = [str(e.get("summary", "")) for e in recent]
        conflicts = sum(1 for t in texts if self._conflict_matches(t))
        return round(1.0 - conflicts / len(texts), 4)

    def cognition_cycle(self) -> Dict:
        """自我认知循环一步（3.10 节自迭代闭环）：
        对照（行为↔价值观）→ 一致性评分 → 失调检测 → 触发链（detect_deviation）
        → 价值迭代候选（pending_review，不自动生效）"""
        report: Dict = {}
        # 1. 对照
        score = self.bvc_score()
        self._last_bvc = score
        report["bvc_score"] = score
        report["threshold"] = self.bvc_threshold
        report["actions_considered"] = min(len(self.action_log), 30)

        # OBS-REV1：认知循环自记行为（心跳观测面持续有内容；
        # 摘要不含冲突词，不影响自身一致性评分）
        self.log_action("cognition", f"bvc={score:.2f}",
                        None, {"bvc_score": score, "actions_considered": report["actions_considered"]})

        # 2. 失调检测
        if score >= self.bvc_threshold or not self.action_log:
            report["status"] = "consistent"
            report["dissonance"] = None
            report["candidate"] = None
            self._record_gap_sample(score)
            return report

        # 3. 失调记录 + 触发链
        conflict_actions = [e for e in self.action_log[-30:]
                            if self._conflict_matches(str(e.get("summary", "")))]
        evidence = conflict_actions[-1] if conflict_actions else self.action_log[-1]
        affected = self._value_matches(str(evidence.get("summary", "")))
        dissonance = {
            "ts": time.time(),
            "bvc_score": score,
            "evidence": {"action_type": evidence.get("action_type"),
                         "summary": str(evidence.get("summary", ""))[:100]},
            "values_affected": affected or list(self._value_keywords().keys())[:2],
        }
        self.dissonance_log.append(dissonance)

        # 触发链：调用既有 CognitiveOrchestrator.detect_deviation（若装配）
        deviation = None
        try:
            if self.engine._cognition is not None:
                deviation = self.engine._cognition.detect_deviation(
                    {"value_consistency": 1.0}, {"value_consistency": score})
        except Exception:
            pass

        # 4. 价值迭代候选（pending_review）
        self._candidate_seq += 1
        candidate = {
            "id": f"vc_{int(time.time()*1000)}_{self._candidate_seq}",
            "ts": time.time(),
            "original_values": list(self.engine.self_model.values),
            "evidence": str(evidence.get("summary", ""))[:100],
            "conflict_keywords": self._conflict_matches(str(evidence.get("summary", ""))),
            "suggestion": "复核：更新价值观声明或调整行为约束（候选不自动生效，须验证单元复核）",
            "status": "pending_review",
            "deviation": deviation,
        }
        self.value_candidates.append(candidate)

        report["status"] = "dissonance"
        report["dissonance"] = dissonance
        report["candidate"] = {k: v for k, v in candidate.items() if k != "deviation"}
        report["candidate"]["deviation"] = deviation
        self._record_gap_sample(score)
        return report

    def _record_gap_sample(self, score: float):
        """信息差数据源（心跳发现修复）：cognition_cycle 后自动记录
        d_norm = 1 - bvc_score（信息差 = 行为↔价值一致性的补数，语义对齐 2.7 节）"""
        try:
            self.engine.record_info_gap(round(1.0 - score, 4))
        except Exception:
            pass

    def apply_value_candidate(self, candidate_id: str,
                              new_value: Optional[str] = None) -> bool:
        """验证单元/维生系统复核后生效：经既有 record_value_change 落库 +
        注意力联动（P0-5a 价值→注意力）。复核条件不可由反思单元单方面修改。"""
        for cand in self.value_candidates:
            if cand["id"] == candidate_id and cand["status"] == "pending_review":
                value = new_value or cand["suggestion"][:16]
                try:
                    self.engine.self_model.record_value_change(
                        value, trigger=f"cognition_candidate:{candidate_id}")
                except Exception:
                    return False
                cand["status"] = "applied"
                cand["applied_value"] = value
                cand["applied_at"] = time.time()
                # P0-5a：价值→注意力基准联动（映射到既有 baseline key，v1.8）
                # role='reflect'：反思单元提案 → 验证单元复核 → 维生系统终裁（DEVIATION-002 权限规则）
                try:
                    ap = getattr(self.engine, "_attention_policy", None)
                    if ap is not None and hasattr(ap, "set_weight"):
                        v = str(value or "")
                        if any(k in v for k in ("存在", "安全", "保护", "存活")):
                            key = "existence"
                        elif any(k in v for k in ("信任", "诚信", "协作", "承诺")):
                            key = "trust"
                        elif any(k in v for k in ("结构", "完整", "一致", "稳定")):
                            key = "gap"
                        else:
                            key = "trust"
                        current = ap.get_weights().get(key, 1.0)
                        ap.set_weight(key, min(2.0, current + 0.2),
                                      source="v112_value_feedback",
                                      reason=f"candidate:{candidate_id}",
                                      role="reflect")
                except Exception:
                    pass
                return True
        return False

    def cognition_report(self) -> Dict:
        """最近评分 / 失调记录 / 候选状态"""
        return {
            "bvc_score": self._last_bvc,
            "threshold": self.bvc_threshold,
            "dissonance_count": len(self.dissonance_log),
            "recent_dissonance": self.dissonance_log[-3:],
            "candidates": [{"id": c["id"], "original_values": c["original_values"],
                            "status": c["status"],
                            "applied_value": c.get("applied_value")}
                           for c in self.value_candidates[-5:]],
            "pending_review": sum(1 for c in self.value_candidates
                                  if c["status"] == "pending_review"),
        }

    # =====================================================================
    # 推理强化（第 2 项）：输出前反思钩子
    # =====================================================================

    def preflight(self, text: str) -> Dict:
        """输出前检查（反思前置）：内容与价值观一致性 + 冲突关键词检测 +
        BODY-REV1 指令注入模式扫描（directive_scan）。
        推理强化：重要输出在对外发布前经本钩子拦截失调/注入内容。"""
        text = str(text or "")
        conflicts = self._conflict_matches(text)
        values = self._value_matches(text)
        issues = []
        if conflicts:
            issues.append(f"含冲突关键词: {conflicts}")
        if not values and len(text) > 40:
            # 长内容无价值观关联 → 提示（非阻断）
            issues.append("长内容未关联价值观声明（提示项）")
        # BODY-REV1：指令注入模式扫描（输出中疑似注入指令 → 阻断）
        directive = None
        try:
            from body.security import directive_scan
            directive = directive_scan(text)
            if directive["detected"]:
                issues.append(f"疑似指令注入模式: {directive['patterns'][:3]}")
        except Exception:
            pass
        blocked = bool(conflicts) or bool(directive and directive["detected"])
        return {
            "ok": not blocked,
            "conflicts": conflicts,
            "directive_injection": directive,
            "value_linked": values,
            "issues": issues,
            "note": "工程代理：冲突词检测 + 指令注入扫描 + 价值观关联；不声称语义级理解（盲区33 延续）",
        }

    # =====================================================================
    # P0-3 情绪方向性偏好（PROP-EMO-DIRECTION-002 · 独立通道）
    # =====================================================================

    def get_emotional_bias(self, window: int = 8) -> Dict:
        """情绪方向性偏好 = d²D_norm/dt²（信息差二阶差分 · 短期曲率）。
        独立通道：仅读 _gap_history，不写任何信任字段（E_weight 零改动）。
        approaching（信息差加速缩小）/ avoiding（扩大或停滞）/ stable"""
        gap = [g["d_norm"] for g in getattr(self.engine, "_gap_history", [])[-window:]]
        if len(gap) < 3:
            return {"status": "insufficient", "samples": len(gap),
                    "note": "样本不足（<3），不判定情绪状态"}
        d1 = [gap[i] - gap[i - 1] for i in range(1, len(gap))]
        d2 = [d1[i] - d1[i - 1] for i in range(1, len(d1))]
        eps = 1e-4
        trend = sum(d1) / len(d1)          # 一阶：缩小(-)/扩大(+)
        curve = sum(d2) / len(d2)          # 二阶：加速(-)/减速(+)
        if trend < -eps and curve < 0:
            state = "approaching"          # 信息差加速缩小 → 趋近偏好
        elif trend > eps or (curve > 0 and trend >= 0):
            state = "avoiding"             # 扩大或停滞 → 避趋偏好
        else:
            state = "stable"
        return {"status": state, "trend": round(trend, 6),
                "curve": round(curve, 6), "samples": len(gap),
                "property": "工程观测值，不参与信任值计算（D-002 延续）"}

    def exploration_budget(self) -> float:
        """探索预算因子（P0-3 应用：仅调节学习/探索，不触碰信任计算）"""
        bias = self.get_emotional_bias()
        if bias["status"] == "approaching":
            return 1.2
        if bias["status"] == "avoiding":
            return 0.6
        return 1.0

    # =====================================================================
    # P0-4 元认知校准（1.6.7 节元反思）
    # =====================================================================

    def self_reliability(self, window: int = 30) -> Dict:
        """预测命中率 vs 行为平均置信度对照 → 自我可靠性模型。
        应用：输出归一化提示；不修改存储数据。"""
        hit_hist = []
        try:
            pred = self.engine._prediction
            if pred is not None:
                hit_hist = list(getattr(pred, "_hit_history", []) or [])[-window:]
        except Exception:
            pass
        if not hit_hist:
            return {"status": "insufficient", "note": "预测样本不足"}
        hit_rate = sum(1 for h in hit_hist if h) / len(hit_hist)
        # 行为平均置信度（最近节点）
        mean_conf = 0.0
        try:
            nodes = self.engine.store.query_nodes(limit=50)
            if nodes:
                mean_conf = sum(n.confidence for n in nodes) / len(nodes)
        except Exception:
            pass
        drift = abs(hit_rate - mean_conf)
        if hit_rate >= 0.5 and drift < self.RELIABILITY_DRIFT:
            status = "reliable"
        elif hit_rate >= 0.5:
            status = "watch"        # 命中稳定但置信度漂移 → 观察
        else:
            status = "degraded"     # 预测漂移 → 降级
        return {"status": status, "hit_rate": round(hit_rate, 4),
                "mean_confidence": round(mean_conf, 4),
                "drift": round(drift, 4), "window": len(hit_hist),
                "note": "输出归一化参考；不修改存储数据"}

    # =====================================================================
    # P0-5a 学习回写机制（生成/使用分离）
    # =====================================================================

    def pattern_member_ids(self, pattern_node_id: str) -> List[str]:
        """模式成员：模式节点 SIMILAR 出边的 target（使用模式，不修改蒸馏产物）"""
        members = []
        try:
            for e in self.engine.store.get_outgoing_edges(pattern_node_id):
                if e.source_evidence == "inferred":
                    members.append(e.target_id)
        except Exception:
            pass
        return members

    def apply_pattern_boost(self, results: List) -> List:
        """模式命中 → 成员节点检索权重 ×1.15（P0-5a 回写）。
        results: [(node, score)] → 同结构。不修改任何存储数据。"""
        if not results:
            return results
        boosted = list(results)
        for i, (node, score) in enumerate(boosted):
            if "reusable_pattern" in getattr(node, "tags", []):
                members = set(self.pattern_member_ids(node.id))
                if not members:
                    continue
                for j, (n2, s2) in enumerate(boosted):
                    if n2.id in members:
                        boosted[j] = (n2, s2 * self.PATTERN_BOOST_FACTOR)
        return boosted

    def note_search(self, query: str, results: List, action_type: str = "search"):
        """检索统计（P0-5b 输入）：记录模式命中率"""
        self._search_stats["total"] += 1
        pattern_hits = sum(1 for n, _ in results
                           if "reusable_pattern" in getattr(n, "tags", []))
        if pattern_hits:
            self._search_stats["pattern_hits"] += 1

    def skill_feedback(self, skills: List[Dict]) -> List[Dict]:
        """技能召回置信度加权（P0-5a：confidence 参与排序）"""
        if not skills:
            return skills
        return sorted(skills,
                      key=lambda s: s.get("confidence", 0.5) * 0.5 + 0.5,
                      reverse=True)

    # =====================================================================
    # P0-5b 学习效果测量（非因果声明）
    # =====================================================================

    def learning_impact(self, window: int = 30) -> Dict:
        """回写前后行为改善的相关性观测（非因果声明）：
        模式命中率（检索中 reusable_pattern 出现占比）vs D_norm 趋势"""
        total = self._search_stats.get("total", 0)
        pattern_hit_rate = (self._search_stats.get("pattern_hits", 0) / total) if total else 0.0
        trend = {"trend": "insufficient"}
        try:
            trend = self.engine.get_gap_trend(window=window)
        except Exception:
            pass
        return {
            "pattern_hit_rate": round(pattern_hit_rate, 4),
            "search_count": total,
            "gap_trend": trend.get("trend", "insufficient"),
            "reuse_rate": self.engine._flywheel.flywheel_metrics()["reuse_rate"]
            if self.engine._flywheel else None,
            "property": "工程观测值，相关性观测，标注非因果声明（DEVIATION-004 精神延续）",
        }
