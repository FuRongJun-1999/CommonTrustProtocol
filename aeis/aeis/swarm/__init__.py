# -*- coding: utf-8 -*-
"""
aeis.swarm · 蜂群协作层（MULTI-INSTANCE-DELIVERY-V1 · 工程实施）
================================================================
六实例蜂群 + 单实例自持的工程基础设施：
  - event_bus.py            事件总线（WAL 持久化 · 延迟分级 · ACK · 签名校验）
  - instance_registry.py    身份注册表 + HMAC 签名 + 写权限
  - trust_aggregator.py     信任聚合（T_avg/T_min/T_variance/T_alignment · 防操纵）
  - survival.py             存活仲裁（三档状态 · 72h 强制休眠 · 回归协议）
  - observer_isolation.py   设计者视角隔离（单向通道 · 动态冷却期 · source 标注）

纯标准库 · 零外部依赖（D-005）。
"""

from .event_bus import EventBus, EVENT_TYPES, DELAY_BANDS, MODE_SELF_SUSTAINING, MODE_INTERNAL_THREAD
from .instance_registry import InstanceRegistry, ROLES, ROLE_CN, TENDENCY
from .trust_aggregator import TrustAggregator, alignment_from
from .survival import SurvivalArbiter, STATE_FULL, STATE_DEGRADED, STATE_MAINTAINED, STATE_SINGLE, STATE_DORMANT
from .observer_isolation import ObserverIsolation

__all__ = [
    "EventBus", "EVENT_TYPES", "DELAY_BANDS", "MODE_SELF_SUSTAINING", "MODE_INTERNAL_THREAD",
    "InstanceRegistry", "ROLES", "ROLE_CN", "TENDENCY",
    "TrustAggregator", "alignment_from",
    "SurvivalArbiter", "STATE_FULL", "STATE_DEGRADED", "STATE_MAINTAINED", "STATE_SINGLE", "STATE_DORMANT",
    "ObserverIsolation",
]
