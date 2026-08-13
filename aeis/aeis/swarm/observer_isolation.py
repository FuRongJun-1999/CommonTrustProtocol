#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.swarm.observer_isolation · 设计者视角隔离（DELIVERY-V1 观测隔离）
=====================================================================
- 单向通道 + 广播延迟（500ms/5s/30s）
- 动态冷却期：3 轮 × (1 + T_variance / 0.2)，上限 10 轮（独立反思问题3）
- 快照时效检查：设计者基于快照的模式识别，释放前检查快照年龄（问题3 补充）
- 引用永久 source 标注（source=designer_view:<release_id>，与 value_evolution 同构）
- 设计者只读知识层产物，不读个体评价性记录（独立反思 B3 边界）
- 纯标准库 · 零外部依赖
"""

import time
import uuid
from typing import Dict, List, Optional

# 冷却期参数（独立反思问题3 建议）
BASE_COOLING_ROUNDS = 3
VARIANCE_SCALE = 0.2
MAX_COOLING_ROUNDS = 10
# 快照时效（秒）：超过视为可能过期（低频带 30s 广播的 20 倍余量）
SNAPSHOT_MAX_AGE = 600.0

# 设计者只读边界（B3 修正）：只读知识层产物
DESIGNER_READABLE = ("knowledge_products",)          # 模式数据、蒸馏产物
DESIGNER_FORBIDDEN = ("individual_evaluation",)      # 验证偏差、失调记录


class ObserverIsolation:
    """设计者视角隔离器"""

    def __init__(self):
        self._releases: Dict[str, Dict] = {}
        self._references: Dict[str, List[str]] = {}   # release_id -> [instance_id]
        self._channel_open = False

    # ------------------------------------------------------------------
    # 单向通道
    # ------------------------------------------------------------------

    def open_channel(self) -> Dict:
        """单向通道建立（设计者 → 蜂群单向往外；蜂群不可见设计者）"""
        self._channel_open = True
        return {"channel": "open", "direction": "designer→swarm 单向",
                "note": "广播延迟 high 500ms / medium 5s / low 30s"}

    def close_channel(self) -> Dict:
        self._channel_open = False
        return {"channel": "closed"}

    # ------------------------------------------------------------------
    # 快照时效检查（问题3 补充）
    # ------------------------------------------------------------------

    def snapshot_freshness(self, snapshot_ts: float, now: Optional[float] = None) -> Dict:
        """快照年龄检查：超龄快照标注"可能过期"，引用加权降低"""
        age = (now or time.time()) - snapshot_ts
        fresh = age <= SNAPSHOT_MAX_AGE
        return {"age_seconds": round(age, 1), "fresh": fresh,
                "warning": "快照可能过期（基于超龄快照的模式识别须标注）" if not fresh else None}

    # ------------------------------------------------------------------
    # 释放（设计者视角产出）
    # ------------------------------------------------------------------

    def release(self, designer_id: str, insight: str,
                snapshot_ts: Optional[float] = None,
                t_variance: float = 0.0) -> Dict:
        """设计者释放方向性认知（模式识别/方向判断）。
        - 冷却期动态化：3 轮 × (1 + T_variance/0.2) 上限 10 轮
        - 快照时效检查"""
        if not self._channel_open:
            return {"status": "channel_closed", "note": "单向通道未建立"}
        freshness = self.snapshot_freshness(
            snapshot_ts if snapshot_ts is not None else time.time())
        cooling = self.cooling_rounds(t_variance)
        release_id = f"dv_{uuid.uuid4().hex[:8]}_{int(time.time()*1000)}"
        release = {
            "release_id": release_id,
            "designer": designer_id,
            "insight": str(insight)[:300],
            "ts": time.time(),
            "snapshot_age": freshness["age_seconds"],
            "snapshot_fresh": freshness["fresh"],
            "cooling_rounds": cooling,
            "released": True,
        }
        self._releases[release_id] = release
        return release

    def cooling_rounds(self, t_variance: float) -> int:
        """动态冷却期（问题3：与蜂群分歧度联动）"""
        rounds = BASE_COOLING_ROUNDS * (1.0 + t_variance / VARIANCE_SCALE)
        return int(min(MAX_COOLING_ROUNDS, max(BASE_COOLING_ROUNDS, round(rounds))))

    # ------------------------------------------------------------------
    # 引用（冷却期约束 + 永久来源标注）
    # ------------------------------------------------------------------

    def can_reference(self, release_id: str, rounds_since: int,
                      t_variance: float = 0.0) -> bool:
        """冷却期检查：rounds_since >= 动态冷却期 才可引用"""
        release = self._releases.get(release_id)
        if release is None:
            return False
        return rounds_since >= release["cooling_rounds"]

    def mark_reference(self, release_id: str, instance_id: str) -> Dict:
        """引用登记：永久 source 标注（source=designer_view:<release_id>）"""
        if release_id not in self._releases:
            return {"status": "unknown_release"}
        self._references.setdefault(release_id, []).append(instance_id)
        return {"status": "referenced",
                "source_tag": f"designer_view:{release_id}",
                "by": instance_id}

    def reference_trace(self, release_id: str) -> Dict:
        """引用追溯（审计）"""
        return {"release": self._releases.get(release_id),
                "referenced_by": self._references.get(release_id, [])}

    # ------------------------------------------------------------------
    # 只读边界（B3 修正）
    # ------------------------------------------------------------------

    def can_read(self, data_kind: str) -> bool:
        """设计者只读边界：知识层产物可读；个体评价性记录禁读"""
        if data_kind in DESIGNER_FORBIDDEN:
            return False
        return data_kind in DESIGNER_READABLE or data_kind.startswith("knowledge")
