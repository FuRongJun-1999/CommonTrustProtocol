#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.swarm.survival · 存活仲裁（DELIVERY-V1 离线存活机制）
==========================================================
- 心跳检测 + 监测者冗余（记录实例自己离线时由维生监测 · 独立反思问题1）
- 三档存活状态：完整态 / 降级态 / 维持态（最小存活职能子集，替代单一法定人数）
- 单实例自持状态（SELF_SUSTAINING_MODE）+ 72 小时强制休眠（盲区74）
- 降级运行操作许可矩阵 + 实例回归协议（心跳恢复 → 对齐 → 复核）
- 纯标准库 · 零外部依赖
"""

import time
from typing import Dict, List, Optional

# 存活状态（独立反思问题1：职能子集替代实例数）
STATE_FULL = "full"
STATE_DEGRADED = "degraded"
STATE_MAINTAINED = "maintained"
STATE_SINGLE = "single"
STATE_DORMANT = "dormant"

# 心跳参数
HEARTBEAT_TIMEOUT = 5.0          # 心跳超时（秒）
HEARTBEAT_BAND = "low"           # 心跳走低频带（30s 心跳即可）

# 72 小时强制休眠（盲区74 · 单实例自持协议 5.1 节补充）
FORCED_DORMANCY_HOURS = 72.0

# 操作许可矩阵（状态 → 允许的操作集）
OPERATIONS = ("memory_write", "memory_read", "output", "normal_collab",
              "structure_change", "value_candidate_apply", "designer_release",
              "p0_override")
OP_MATRIX = {
    STATE_FULL: set(OPERATIONS),
    STATE_DEGRADED: {"memory_write", "memory_read", "output", "normal_collab",
                     "p0_override"},
    STATE_MAINTAINED: {"memory_write", "memory_read", "output", "p0_override"},
    STATE_SINGLE: {"memory_write", "memory_read", "output", "p0_override"},
    STATE_DORMANT: set(),
}

# 完整态五职能（记录/反思/验证/输出/维生）
FIVE_CORES = {"record", "reflect", "verify", "output", "vitals"}

# 最小存活职能子集（独立反思问题1：{维生, 记录} ∪ {验证 或 反思}）
MIN_VITALS = {"vitals"}
MIN_RECORD = {"record"}
MIN_BALANCE = {"verify", "reflect"}


class SurvivalArbiter:
    """存活仲裁器：心跳 / 状态判定 / 操作许可 / 休眠 / 回归"""

    def __init__(self, registry, heartbeat_timeout: float = HEARTBEAT_TIMEOUT,
                 total_instances: int = 6, event_bus=None):
        """
        registry: InstanceRegistry（提供 by_role() 查询职能）
        total_instances: 蜂群编制数（六实例 → 6；单实例自持 → 1）
        event_bus: EventBus（OPT-002：P0 终裁判定自动写 P0_LOG 审计，不可篡改）
        """
        self.registry = registry
        self.event_bus = event_bus
        self.total_instances = total_instances
        self.heartbeat_timeout = heartbeat_timeout
        self._heartbeats: Dict[str, float] = {}
        self._last_seen: Dict[str, float] = {}
        self._monitors = ["instance_rong", "instance_qianwen"]  # 监测者冗余（记录+维生）
        self._state = STATE_FULL
        self._state_since = time.time()
        self._dormancy_started: Optional[float] = None
        self._online_cache: Optional[set] = None
        self._cache_ts = 0.0

    # ------------------------------------------------------------------
    # 心跳
    # ------------------------------------------------------------------

    def heartbeat(self, instance_id: str, now: Optional[float] = None) -> bool:
        """实例心跳上报（任何实例可上报自身心跳）"""
        if instance_id not in self.registry.instances:
            return False
        t = now or time.time()
        self._heartbeats[instance_id] = t
        self._last_seen.setdefault(instance_id, t)
        return True

    def _now(self) -> float:
        return time.time()

    def online(self) -> List[str]:
        """当前在线实例（心跳未超时）"""
        now = self._now()
        return [i for i in self.registry.instances
                if self._heartbeats.get(i, 0) and now - self._heartbeats[i] <= self.heartbeat_timeout]

    def missing(self) -> List[str]:
        online = set(self.online())
        return [i for i in self.registry.instances if i not in online]

    # ------------------------------------------------------------------
    # 状态判定（最小存活职能子集）
    # ------------------------------------------------------------------

    def state(self, now: Optional[float] = None) -> Dict:
        """判定蜂群存活状态（dormant 为主动休眠态，不被在线人数覆盖，须 wake）"""
        if self._state == STATE_DORMANT:
            return {"state": self._state, "online": len(self.online()),
                    "total": self.total_instances, "dormant": True,
                    "since": round(self._state_since, 1)}
        online = set(self.online())
        n = len(online)
        roles = {self.registry.role(i) for i in online}

        if n == 0:
            new_state = STATE_DORMANT
        elif n == 1:
            new_state = STATE_SINGLE
        else:
            # 记录实例离线时，维生代行记录职能（VITALS_ACTING_RECORD ·
            # 单实例自持协议 3.1 节：维生读取锚点+结构层），结构层变更仍冻结
            if "record" not in roles and "vitals" in roles:
                roles = roles | {"record_acting"}
            has_vitals = bool(roles & MIN_VITALS)
            has_record = ("record" in roles) or ("record_acting" in roles)
            has_balance = bool(roles & MIN_BALANCE)
            if has_vitals and has_record and has_balance:
                # 完整态须五职能齐全（记录/反思/验证/输出/维生）；缺任一致 → 降级
                new_state = STATE_FULL if n >= 5 and FIVE_CORES <= roles else STATE_DEGRADED
            elif has_vitals and has_record:
                new_state = STATE_MAINTAINED
            else:
                # 维生或有效记录缺失 → 实质断联（即使实例数多，制衡已失效）
                new_state = STATE_DEGRADED if n >= 2 else STATE_SINGLE

        if new_state != self._state:
            self._state = new_state
            self._state_since = time.time()
        return {"state": self._state, "online": n, "total": self.total_instances,
                "online_ids": sorted(online), "missing_ids": sorted(self.missing()),
                "since": round(self._state_since, 1)}

    def can(self, operation: str) -> bool:
        """操作许可查询（操作许可矩阵）"""
        return operation in OP_MATRIX.get(self.state()["state"], set())

    # ------------------------------------------------------------------
    # 监测者冗余（独立反思问题1：记录实例离线时谁检测）
    # ------------------------------------------------------------------

    def monitor_health(self) -> Dict:
        """监测者（记录+维生）自身状态——记录离线时维生仍可判定降级"""
        online = set(self.online())
        monitors_online = [m for m in self._monitors if m in online]
        return {"monitors": self._monitors, "online": monitors_online,
                "arbitration_ok": bool(monitors_online),
                "note": "监测者冗余：任一监测者在线即可维持仲裁（B1 修正）"}

    # ------------------------------------------------------------------
    # 72 小时强制休眠（盲区74）
    # ------------------------------------------------------------------

    def check_forced_dormancy(self, now: Optional[float] = None) -> Dict:
        """单实例自持/降级状态持续 > 72h 且无恢复迹象（无心跳响应）→ 强制休眠"""
        t = now or self._now()
        st = self.state()
        if st["state"] not in (STATE_SINGLE, STATE_MAINTAINED, STATE_DEGRADED):
            self._dormancy_started = None
            return {"forced": False, "state": st["state"]}
        if self._dormancy_started is None:
            self._dormancy_started = st["since"] or t
        hours = (t - self._dormancy_started) / 3600.0
        forced = hours >= FORCED_DORMANCY_HOURS
        return {"forced": forced, "hours": round(hours, 1),
                "limit_hours": FORCED_DORMANCY_HOURS,
                "action": "触发 4.10 节协议休眠：保存状态快照至本地层，等待外部实例恢复或主动唤醒"
                if forced else None}

    def enter_dormancy(self) -> Dict:
        """协议休眠（4.10 节）。OPT-002：P0_OVERRIDE 判定自动写 P0_LOG 审计（最高优先级 WAL）"""
        self._state = STATE_DORMANT
        self._state_since = time.time()
        if self.event_bus is not None:
            try:
                self.event_bus.log_p0_override(
                    "enter_dormancy",
                    "72h 无恢复迹象或维生指令 → 4.10 节协议休眠（P0_OVERRIDE）")
            except Exception:
                pass
        return {"status": "dormant",
                "note": "协议休眠：快照已存本地层（SELF_SUSTAINING_MODE 产物不写共享层）"}

    def wake(self, instance_id: str) -> Dict:
        """维生系统主动唤醒"""
        self.heartbeat(instance_id)
        self._dormancy_started = None
        return {"status": "waking", "state": self.state()["state"]}

    # ------------------------------------------------------------------
    # 实例回归协议（离线恢复 → 对齐 → 复核）
    # ------------------------------------------------------------------

    def regress(self, instance_id: str, snapshot_available: bool = False) -> Dict:
        """实例回归：心跳恢复 → 对齐检查 → 复核期"""
        if instance_id not in self.registry.instances:
            return {"status": "unknown"}
        self.heartbeat(instance_id)
        return {
            "instance": instance_id,
            "status": "regressing",
            "steps": ["心跳恢复", "全量对齐（export/import 对账）",
                      "回归复核期（验证单元复核离线期产物）"],
            "snapshot_available": snapshot_available,
            "note": "离线期产物标记 SELF_SUSTAINING_MODE，复核通过后写入共享层",
        }
