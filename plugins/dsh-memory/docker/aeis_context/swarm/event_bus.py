#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.swarm.event_bus · 蜂群事件总线（MULTI-INSTANCE-DELIVERY-V1）
================================================================
- WAL 持久化（append-only，重启恢复）
- 延迟分级：高频 500ms / 中频 5s / 低频 30s
- 广播 ACK（确认制）+ 未确认追踪
- 事件类型 schema（STRUCTURE_UPDATE 等 9 类）
- INTERNAL_THREAD 标记（单实例内部并行模拟 · 2.4 节）
- 消息签名校验（配合 instance_registry）
- 纯标准库 · 零外部依赖（D-005）
"""

import hashlib
import json
import os
import threading
import time
from typing import Callable, Dict, List, Optional

# 事件类型（3.1 节事件通信 + 存活扩展）
EVENT_TYPES = (
    "STRUCTURE_UPDATE",   # 结构层变更（记录实例主控）
    "PROPOSAL_SUBMIT",    # 提案提交（反思实例）
    "VERIFICATION_RESULT",# 验证结果（验证实例）
    "TRUST_SNAPSHOT",     # 信任快照（记录实例聚合广播）
    "CONDITION_SWITCH",   # 条件空间切换（→验证复核→记录结构层）
    "P0_CRISIS",          # P0 危机（→维生终裁）
    "P0_LOG",             # P0_OVERRIDE 强制审计（OPT-002 · 最高持久化优先级）
    "DESIGNER_VIEW",      # 设计者视角释放（临时设计者·只读）
    "HEARTBEAT",          # 心跳（存活监测）
    "INSTANCE_JOIN",      # 实例加入
    "INSTANCE_LEAVE",     # 实例离开
    # ---- 对抗安全（ADVERSARIAL-GUARDRAIL · DEVIATION-010 关闭） ----
    "ADVERSARIAL_SIGNAL",      # 对抗信号检测（疑似入侵/敌意行为）
    "ACTION_BLOCKED",          # 动作分级拦截（越权/未授权破坏级动作）
    "COUNTERATTACK_BLOCKED",   # 不反击拦截（报复性动作被阻断——最高优先）
    "COOLDOWN_ENTERED",        # 冷静期进入（对抗信号后冻结 N 轮）
)

# 延迟分级（工程默认值 · DELIVERY-V1 通信延迟参数）
DELAY_BANDS = {"high": 0.5, "medium": 5.0, "low": 30.0}

# 单实例自持/内部并行模拟标记
MODE_SELF_SUSTAINING = "SELF_SUSTAINING_MODE"
MODE_INTERNAL_THREAD = "INTERNAL_THREAD"

# OPT-003：共享层事件强制签名（sign=False 不可绕过，防记录实例被 compromise 后伪造广播）
FORCE_SIGN_TYPES = ("STRUCTURE_UPDATE", "CONDITION_SWITCH",
                    "P0_CRISIS", "P0_LOG", "TRUST_SNAPSHOT")

# OPT-001：广播前验证拦截的默认事件类型（CONDITION_SWITCH → 验证实例签章前置）
DEFAULT_VERIFY_TYPES = ("CONDITION_SWITCH",)


class EventBus:
    """蜂群事件总线：WAL 持久化 + 延迟分级 + ACK 确认制"""

    def __init__(self, node_id: str, wal_path: Optional[str] = None,
                 registry=None):
        """
        node_id: 本节点实例 id（如 instance_qianwen）
        wal_path: WAL 文件路径（None → 不持久化，仅内存）
        registry: InstanceRegistry（提供 verify() 做签名校验；None → 跳过校验）
        """
        self.node_id = node_id
        self.wal_path = wal_path
        self.registry = registry
        # OPT-001：广播前验证拦截钩子（event_type -> Callable[[event], bool]）
        self.verify_hooks: Dict[str, Callable[[Dict], bool]] = {}
        self._seq = 0
        self._lock = threading.Lock()
        self._subscribers: Dict[str, List[Callable]] = {t: [] for t in EVENT_TYPES}
        self._acked: Dict[str, set] = {}        # event_id -> {instance_id}
        self._delivered: Dict[str, float] = {}  # event_id -> ts（延迟测量）
        self._wal_fp = None
        self._replayed = 0
        if wal_path:
            os.makedirs(os.path.dirname(wal_path), exist_ok=True) if os.path.dirname(wal_path) else None
            self._wal_fp = open(wal_path, "a", encoding="utf-8")
            self._replay()

    # ------------------------------------------------------------------
    # 发布与订阅
    # ------------------------------------------------------------------

    def publish(self, event_type: str, payload: Dict,
                source: Optional[str] = None, band: str = "medium",
                mode: Optional[str] = None, sign: bool = True) -> Dict:
        """发布事件。band: high(500ms)/medium(5s)/low(30s)。
        mode: SELF_SUSTAINING_MODE / INTERNAL_THREAD（单实例自持标记）。
        OPT-003：共享层事件（STRUCTURE_UPDATE/CONDITION_SWITCH/P0_CRISIS/P0_LOG/TRUST_SNAPSHOT）
        强制签名（sign=False 不可绕过）。
        OPT-001：CONDITION_SWITCH 等配置了验证拦截钩子的事件，广播前必须通过验证实例签章；
        拦截拒绝 → 不发布、不入 WAL（返回 {"status": "rejected"}）。"""
        assert event_type in EVENT_TYPES, f"unknown event type: {event_type}"
        assert band in DELAY_BANDS, f"unknown band: {band}"
        # OPT-003：共享层事件强制签名（不可绕过）
        if event_type in FORCE_SIGN_TYPES:
            sign = True
        with self._lock:
            self._seq += 1
            event = {
                "id": f"ev_{int(time.time()*1000)}_{self._seq}",
                "seq": self._seq,
                "ts": time.time(),
                "type": event_type,
                "source": source or self.node_id,
                "payload": payload,
                "band": band,
                "delay": DELAY_BANDS[band],
                "mode": mode,           # None | SELF_SUSTAINING_MODE | INTERNAL_THREAD
                "sig": None,
            }
            if sign and self.registry is not None:
                event["sig"] = self.registry.sign(
                    self._signable(event), event["source"])
            # OPT-001：广播前验证拦截（验证实例签章前置，非事后订阅）
            hook = self.verify_hooks.get(event_type)
            if hook is not None:
                if not hook(dict(event)):
                    return {"status": "rejected",
                            "reason": "verify_hook_rejected",
                            "event_type": event_type}
        self._wal_append(event)
        self._dispatch(event)
        return event

    def set_verify_hook(self, event_type: str, hook: Optional[Callable[[Dict], bool]]):
        """OPT-001：设置/清除广播前验证拦截钩子（返回 True 放行，False 拒绝发布）。
        典型用法：验证实例（Kimi）的 CONDITION_SWITCH 复核回调。"""
        assert event_type in EVENT_TYPES
        if hook is None:
            self.verify_hooks.pop(event_type, None)
        else:
            self.verify_hooks[event_type] = hook

    # ------------------------------------------------------------------
    # OPT-002：P0_OVERRIDE 强制审计日志（不可篡改 · 最高持久化优先级）
    # ------------------------------------------------------------------

    def log_p0_override(self, directive: str, note: str = "",
                        source: Optional[str] = None) -> Dict:
        """P0_OVERRIDE 判定强制审计：自动写入 WAL（append-only 不可篡改），
        标记最高持久化优先级。任何 P0 终裁路径应调用本方法。"""
        ev = self.publish(
            "P0_LOG",
            {"directive": directive, "note": str(note)[:200],
             "override_mark": "P0_OVERRIDE",
             "priority": "highest"},
            source=source, band="high",
            mode=MODE_SELF_SUSTAINING,
            sign=True)
        return ev

    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件（callback(event)）"""
        assert event_type in EVENT_TYPES
        self._subscribers[event_type].append(callback)

    def _dispatch(self, event: Dict):
        for cb in list(self._subscribers.get(event["type"], [])):
            try:
                cb(event)
            except Exception:
                pass
        # 本节点自动确认
        if self.registry is not None:
            self.ack(event["id"], self.node_id)

    # ------------------------------------------------------------------
    # 签名校验（防伪造广播 · B2 盲区修正）
    # ------------------------------------------------------------------

    @staticmethod
    def _signable(event: Dict) -> str:
        return json.dumps({k: event[k] for k in
                           ("seq", "ts", "type", "source", "payload", "band", "mode")},
                          ensure_ascii=False, sort_keys=True)

    def verify_event(self, event: Dict) -> bool:
        """校验事件签名（未配置 registry → 放行）"""
        if self.registry is None or not event.get("sig"):
            return True
        return self.registry.verify(self._signable(event), event["sig"], event["source"])

    def verify_all_events(self) -> Dict:
        """全量签名校验（安全审计）"""
        ok = bad = 0
        for ev in self._iter_wal():
            if self.verify_event(ev):
                ok += 1
            else:
                bad += 1
        return {"verified": ok, "forged": bad}

    # ------------------------------------------------------------------
    # ACK 确认制
    # ------------------------------------------------------------------

    def ack(self, event_id: str, by: str):
        """实例确认收到事件"""
        with self._lock:
            self._acked.setdefault(event_id, set()).add(by)

    def pending_acks(self, event_id: str, total_instances: int = 0) -> List[str]:
        """未确认的实例列表（优先注册表真实实例；无注册表时退回 instance_i 模式）"""
        acked = self._acked.get(event_id, set())
        known = self._known_instances(total_instances)
        return [i for i in known if i not in acked]

    def _known_instances(self, total: int) -> List[str]:
        if self.registry is not None and self.registry.instances:
            return list(self.registry.instances.keys())
        return [f"instance_{i}" for i in range(1, max(1, total) + 1)]

    def latency_ms(self, event_id: str, now: Optional[float] = None) -> Optional[float]:
        """事件投递延迟（模拟：从发布到查询的经过时间）"""
        ev = self.get(event_id)
        if ev is None:
            return None
        return round(((now or time.time()) - ev["ts"]) * 1000, 1)

    # ------------------------------------------------------------------
    # WAL 持久化
    # ------------------------------------------------------------------

    def _wal_append(self, event: Dict):
        if self._wal_fp is None:
            return
        line = json.dumps(event, ensure_ascii=False)
        with self._lock:
            self._wal_fp.write(line + "\n")
            self._wal_fp.flush()

    def _replay(self):
        """启动时从 WAL 恢复（恢复 seq + 重新分发未确认事件）"""
        if not self.wal_path or not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._seq = max(self._seq, ev.get("seq", 0))
                self._replayed += 1

    def _iter_wal(self) -> List[Dict]:
        if not self.wal_path or not os.path.exists(self.wal_path):
            return []
        events = []
        with open(self.wal_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events

    def get(self, event_id: str) -> Optional[Dict]:
        for ev in self._iter_wal():
            if ev.get("id") == event_id:
                return ev
        return None

    def seq_check(self) -> Dict:
        """乱序检查：seq 应单调递增"""
        seqs = [ev["seq"] for ev in self._iter_wal()]
        monotonic = all(seqs[i] < seqs[i + 1] for i in range(len(seqs) - 1))
        return {"events": len(seqs), "monotonic": monotonic,
                "replayed": self._replayed}

    def stats(self) -> Dict:
        return {"seq": self._seq, "wal": self.wal_path,
                "replayed": self._replayed,
                "events": len(self._iter_wal())}

    def close(self):
        if self._wal_fp:
            self._wal_fp.close()
            self._wal_fp = None
