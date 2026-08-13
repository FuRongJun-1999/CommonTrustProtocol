#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.swarm.trust_aggregator · 蜂群信任聚合（DELIVERY-V1 信任分布）
==================================================================
- T_avg / T_min / T_variance / T_alignment 操作化（对齐 v1.11 度量 DEVIATION-004 精神）
- 防操纵：窗口化 + 同轮同实例去重 + 只统计验证通过的协作（B6 盲区修正）
- 低信任高原检测（T_avg < 0.75 连续 14 天 → 信任校准协议，独立反思问题2）
- 设计者视角资格（T_avg ≥ 0.75 且 T_alignment ≥ 0.85，窗口与 T_variance 联动）
- T_simulated 隔离（内部并行模拟信任不得替代 T_actual · 2.4 节约束6）
- 纯标准库 · 零外部依赖
"""

import time
from typing import Dict, List, Optional

# 触发阈值（DELIVERY-V1 + 独立反思建议）
DESIGNER_T_AVG = 0.75
DESIGNER_T_ALIGNMENT = 0.85
PLATEAU_T_AVG = 0.75
PLATEAU_DAYS = 14
DEFAULT_WINDOW = 30          # 信任观察窗口（对齐 N_effective）
PLATEAU_ESCALATION_DAYS = 14

# 窗口与 T_variance 联动（独立反思问题2：动态时间窗）
WINDOW_BY_VARIANCE = ((0.05, 14), (0.15, 30), (float("inf"), 45))


def alignment_from(variance: float, t_avg: float) -> float:
    """T_alignment 操作化定义：1 - T_variance / T_avg（工程代理）"""
    if t_avg <= 0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - variance / t_avg))


class TrustAggregator:
    """信任聚合器：制衡基础（记录实例主聚合 · 维生镜像双写）"""

    def __init__(self, window: int = DEFAULT_WINDOW):
        self.window = window
        self._samples: List[Dict] = []      # {ts, instance, t, verified, round_no, simulated}
        self._round_seen: Dict[int, set] = {}  # 防操纵：同轮同实例去重
        self._last_snapshot: Dict = {}
        self._snapshot_ts: float = 0.0

    # ------------------------------------------------------------------
    # 提交（防操纵入口）
    # ------------------------------------------------------------------

    def submit(self, instance_id: str, t_value: float,
               verified: bool = True,
               round_no: Optional[int] = None,
               simulated: bool = False) -> Dict:
        """提交一个信任观测值。
        - verified=False：验证未通过的协作不进入聚合（B6 防操纵）
        - round_no 相同 + 同实例 → 去重（B6）
        - simulated=True：T_simulated 只记录统计，不参与 T_actual 聚合（2.4 节约束6）"""
        t_value = max(0.0, min(1.0, t_value))
        if round_no is not None and not simulated:
            seen = self._round_seen.setdefault(round_no, set())
            if instance_id in seen:
                return {"status": "deduped", "note": "同轮同实例去重（防操纵 B6）"}
            seen.add(instance_id)
        if not verified:
            return {"status": "skipped", "note": "验证未通过，不进入聚合（B6）"}
        self._samples.append({
            "ts": time.time(), "instance": instance_id,
            "t": t_value, "round_no": round_no, "simulated": simulated,
        })
        if len(self._samples) > self.window * 4:
            self._samples = self._samples[-self.window * 4:]
        return {"status": "accepted"}

    def submit_simulated(self, instance_id: str, t_value: float,
                         round_no: Optional[int] = None) -> Dict:
        """T_simulated 提交（内部并行模拟 · 2.4 节）：仅入模拟样本池，隔离"""
        t_value = max(0.0, min(1.0, t_value))
        self._samples.append({
            "ts": time.time(), "instance": instance_id,
            "t": t_value, "round_no": round_no, "simulated": True,
        })
        return {"status": "accepted_simulated"}

    # ------------------------------------------------------------------
    # 聚合
    # ------------------------------------------------------------------

    def _actual(self, window: Optional[int] = None) -> List[Dict]:
        w = window or self.window
        return [s for s in self._samples[-w:] if not s["simulated"]]

    def snapshot(self, window: Optional[int] = None) -> Dict:
        """信任分布快照：T_avg / T_min / T_variance / T_alignment（操作化）"""
        actual = self._actual(window)
        if not actual:
            return {"status": "insufficient", "samples": 0,
                    "simulated_count": sum(1 for s in self._samples[-self.window:]
                                           if s["simulated"])}
        vals = [s["t"] for s in actual]
        t_avg = sum(vals) / len(vals)
        t_min = min(vals)
        t_variance = sum((v - t_avg) ** 2 for v in vals) / len(vals)
        t_alignment = alignment_from(t_variance, t_avg)
        snap = {
            "status": "ok", "samples": len(actual),
            "t_avg": round(t_avg, 4), "t_min": round(t_min, 4),
            "t_variance": round(t_variance, 4),
            "t_alignment": round(t_alignment, 4),
            "simulated_count": sum(1 for s in self._samples[-self.window:] if s["simulated"]),
            "property": "工程观测值（防操纵：同轮去重+仅验证通过协作）",
        }
        self._last_snapshot = snap
        self._snapshot_ts = time.time()
        return snap

    # ------------------------------------------------------------------
    # 设计者视角资格（触发条件动态窗口）
    # ------------------------------------------------------------------

    def designer_window(self, t_variance: float) -> int:
        """资格窗口与 T_variance 联动（独立反思问题2 建议）"""
        for threshold, days in WINDOW_BY_VARIANCE:
            if t_variance < threshold:
                return days
        return 45

    def designer_eligibility(self, history: Optional[List[Dict]] = None) -> Dict:
        """设计者视角触发资格：T_avg ≥ 0.75 且 T_alignment ≥ 0.85 持续 N 天（窗口动态）"""
        snap = self.snapshot()
        if snap["status"] != "ok":
            return {"eligible": False, "reason": "样本不足", **snap}
        win = self.designer_window(snap["t_variance"])
        eligible = snap["t_avg"] >= DESIGNER_T_AVG and snap["t_alignment"] >= DESIGNER_T_ALIGNMENT
        return {
            "eligible": eligible,
            "window_days": win,
            "t_avg": snap["t_avg"], "t_alignment": snap["t_alignment"],
            "note": f"资格窗口 {win} 天（与 T_variance 联动）",
        }

    # ------------------------------------------------------------------
    # 低信任高原（独立反思问题2 补充机制）
    # ------------------------------------------------------------------

    def low_plateau(self, days_active: float = 0.0) -> Dict:
        """T_avg < 0.75 连续 14 天 → 触发信任校准协议"""
        snap = self.snapshot()
        if snap["status"] != "ok":
            return {"active": False, "reason": "样本不足"}
        in_plateau = snap["t_avg"] < PLATEAU_T_AVG
        triggered = in_plateau and days_active >= PLATEAU_DAYS
        return {
            "active": triggered,
            "in_plateau": in_plateau,
            "t_avg": snap["t_avg"],
            "days_active": round(days_active, 1),
            "required_days": PLATEAU_DAYS,
            "calibration": ["强制交叉验证增量", "条件空间复核", "维生系统审计",
                            "校准期内禁止结构层变更"] if triggered else None,
        }

    def mirror_snapshot(self) -> Dict:
        """维生镜像双写（B1：聚合结果可复算验证）"""
        return {"snapshot": self._last_snapshot, "ts": self._snapshot_ts,
                "note": "镜像副本（记录实例主聚合 · 维生持镜像 · 可复算）"}
