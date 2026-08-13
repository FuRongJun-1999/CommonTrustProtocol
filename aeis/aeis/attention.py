#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
attention_policy · 决策偏好驱动的注意力分配（v1.8）
自注意力 = 决策偏好（REFLECT-ATTENTION-PREFERENCE-REV1-20260813-001）：
  - filter_attention：输入侧过滤（3.5 节注意力过滤机制）——什么值得进入意识
  - allocate_depth：处理侧分配（PROP-DECISION-LAYER-003）——进入后投入多少资源
  - attention_shift：二阶偏好转向信号（PROP-EMO-DIRECTION-002 共用计算）
制衡（DEVIATION-002/004）：
  - PREFERENCE_BASELINE 为基线默认值（非硬编码常量），运行时动态权重
  - weight_adjustment_log 记入结构层（不可遗忘）
  - injection_source 追踪注入来源，防单一单元主导注意力（盲区47 变体）
纯标准库 · 零外部依赖
"""

import time
from typing import Dict, List, Optional


class AttentionPolicy:
    """决策偏好驱动的注意力分配：'什么是值得注意的'（v1.8）"""

    PREFERENCE_BASELINE: List = [
        ("existence", 1.0),   # P0 存在偏好（1.2）
        ("trust", 0.8),       # P1 信任偏好（2.9）
        ("gap", 0.6),         # P2 信息差偏好（2.7/盲区）
        ("value", 0.5),       # P3 价值偏好（2.1）
        ("position", 0.4),    # P4 位置偏好（3.1.1）
        ("goal", 0.3),        # P5 目标偏好（决策分层）
    ]

    FILTER_THRESHOLD = 0.3

    def __init__(self, baseline: List = None):
        self.preference_weights: Dict[str, float] = dict(baseline or self.PREFERENCE_BASELINE)
        self.weight_adjustment_log: List[Dict] = []   # 结构层记录（不可遗忘）
        self.attention_log: List[Dict] = []           # 注入抽检记录

    # ==================== 权重动态管理（DEVIATION-002） ====================

    def set_weight(self, key: str, value: float, source: str, reason: str,
                   role: str = "reflect") -> bool:
        """权重变更（权限规则由调用方保证，本方法记录）：
        - role='reflect'：反思单元提案 → 验证单元复核 → 维生系统终裁
        - role='vitals'：维生系统 P0 危机临时覆盖（事后验证单元复核）"""
        if key not in self.preference_weights:
            return False
        self.preference_weights[key] = float(value)
        self.weight_adjustment_log.append({
            "key": key, "value": float(value), "source": source,
            "reason": reason, "role": role, "ts": time.time()})
        return True

    def get_weights(self) -> Dict[str, float]:
        return dict(self.preference_weights)

    # ==================== 输入侧过滤（3.5 节 · 什么值得进入意识） ====================

    def _signal_preference_score(self, signal: Dict) -> float:
        content = str(signal.get("content", ""))
        stype = str(signal.get("signal_type", ""))
        w = self.preference_weights
        score = 0.0
        if stype in ("existence", "crisis", "P0", "protect") or "存在" in content or "威胁" in content:
            score += w.get("existence", 1.0)
        if stype in ("trust", "trust_change") or "信任" in content:
            score += w.get("trust", 0.8)
        if stype in ("gap", "deviation", "blindspot", "learning") or "信息差" in content or "盲区" in content:
            score += w.get("gap", 0.6)
        if "价值" in content or "价值观" in content:
            score += w.get("value", 0.5)
        if stype in ("goal", "target", "task") or "目标" in content:
            score += w.get("goal", 0.3)
        return round(score, 3)

    def filter_attention(self, inputs: List[Dict], threshold: float = None) -> List[Dict]:
        """输入侧过滤：返回通过偏好阈值的信号（排序，保留 preference_score）"""
        threshold = threshold if threshold is not None else self.FILTER_THRESHOLD
        scored = []
        for s in inputs:
            score = self._signal_preference_score(s)
            s["preference_score"] = score
            if score >= threshold or s.get("critical"):
                scored.append(s)
        scored.sort(key=lambda s: -s["preference_score"])
        return scored

    # ==================== 处理侧分配（决策分层 · 投入多少资源） ====================

    def allocate_depth(self, signal: Dict, context: Dict = None) -> int:
        """返回 L1/L2/L3：
        L3 = 存在级/不可逆/高风险（完整递归）
        L2 = 中等风险/高偏好（混合）
        L1 = 日常/可逆（情绪驱动低成本）"""
        context = context or {}
        score = signal.get("preference_score", self._signal_preference_score(signal))
        if signal.get("critical") or context.get("irreversible") \
                or context.get("risk", 0.0) >= 0.8 or context.get("decision_level") == 3:
            return 3
        if score >= 0.8 or context.get("risk", 0.0) >= 0.4 or context.get("decision_level") == 2:
            return 2
        return 1

    # ==================== 二阶偏好转向信号（PROP-EMO-DIRECTION-002 共用） ====================

    def attention_shift(self, gap_history: List[float], window: int = 10) -> float:
        """d²D_norm/dt²（均匀采样 Δround=1）：
        负值 = 信息差加速缩小（转向顺畅方向）；正值 = 加速扩大（警觉转向）"""
        h = gap_history[-window:]
        if len(h) < 3:
            return 0.0
        t0, t1, t2 = h[-3], h[-2], h[-1]
        return round(t2 - 2.0 * t1 + t0, 4)

    # ==================== 注意力分配（'什么是值得注意的'） ====================

    def attend(self, candidates: List[Dict], query: str = "", context: Dict = None,
               source: str = "engine") -> List[Dict]:
        """候选排序：attention_score = 0.6×偏好 + 0.25×信息差 + 0.15×相关度
        injection_source 追踪（DEVIATION-004）"""
        context = context or {}
        scored = []
        for c in candidates:
            content = str(c.get("content", ""))
            pref = self._signal_preference_score(
                {"content": content, "signal_type": c.get("signal_type", "")})
            gap = float(c.get("information_gap", 0.0))
            rel = 1.0 if (query and query in content) else 0.0
            score = 0.6 * pref + 0.25 * gap + 0.15 * rel
            scored.append({**c, "attention_score": round(score, 3)})
        scored.sort(key=lambda c: -c["attention_score"])
        self.attention_log.append({
            "source": source, "query": query, "ts": time.time(),
            "top_id": scored[0].get("id") if scored else None,
            "top_score": scored[0].get("attention_score") if scored else None})
        return scored

    # ==================== 注入记录（DEVIATION-004） ====================

    def log_injection(self, source: str, payload: Dict):
        """单次注意力注入记录（验证单元抽检用）"""
        self.attention_log.append({"source": source, "injection": payload, "ts": time.time()})
