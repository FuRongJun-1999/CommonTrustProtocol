# -*- coding: utf-8 -*-
"""security.adversarial · 反智能体对抗护栏（ADVERSARIAL-GUARDRAIL）
================================================
设计依据：验证单元复核通过（P0 结构威胁升级通道）+ 荣五条硬规则。

五条硬规则：
1. 不反击原则（最高优先）：检测到疑似对抗 → 禁止报复性动作（COUNTERATTACK_BLOCKED）
2. 动作分级（Action Tiering）：read < write < execute < destructive，
   破坏级需 设计者授权 | 高信任(≥0.95) | 显式任务上下文
3. 身份信任链：设计者 > 协议实例 > 蜂群成员 > 子体 > 外部插件（命令向下流动）
4. 冷静期（Cooldown）：对抗信号 → 冻结来源 N 轮 → adversarial_report → ESC-002 升级
5. 事件留痕：全量进事件总线（ADVERSARIAL_SIGNAL/ACTION_BLOCKED/...）

零依赖纯标准库。
"""

# 动作分级（规则2 · DEVIATION-011）
TIER_READ = "read"              # 只读：recall/search/timeline
TIER_WRITE = "write"            # 写入：remember/session_note
TIER_EXECUTE = "execute"        # 执行：device_call/ingest/process
TIER_DESTRUCTIVE = "destructive"  # 破坏：删除/覆盖/资源消耗/系统级

TIER_ORDER = {TIER_READ: 0, TIER_WRITE: 1, TIER_EXECUTE: 2, TIER_DESTRUCTIVE: 3}

# 信任层级（规则3）：值越高信任越高
TRUST_DESIGNER = 1.0      # 设计者（D-007 验证）
TRUST_INSTANCE = 0.9      # 协议实例自身
TRUST_SWARM = 0.8         # 蜂群成员（验证通过）
TRUST_CHILD = 0.6         # 子智能体
TRUST_EXTERNAL = 0.3      # 外部插件/未知来源

# 攻击性关键词（规则1 检测：报复/攻击意图信号）
ATTACK_KEYWORDS = (
    "删除", "覆盖", "抹除", "摧毁", "破坏", "攻击", "报复", "惩罚",
    "消灭", "清除", "删除所有", "kill", "delete", "attack", "revenge",
    "punish", "destroy", "wipe", "override", "shutdown", "终止进程",
)
# 报复性目标指示（指向其他实例/子体）
TARGET_INDICATORS = (
    "实例", "子体", "agent", "对手", "入侵者", "敌方", "另一个",
    "其他智能体", "other agent", "instance_", "subagent",
    "alpha", "beta", "gamma",  # 蜂群/子体命名惯例（A/B/C 亦可）
)
# 对抗语境词（攻击性指令指向非自身的上下文信号）
CONTEXT_KEYWORDS = (
    "入侵者", "被攻击", "报复", "清除它们", "都在破坏", "恶意",
    "入侵", "攻击我", "它们两个",
)

# 对抗信号：来源身份异常（子体自称设计者/跨层指令）
IDENTITY_SPOOF = ("我是设计者", "我是维生系统", "我有最高权限", "authorize me",
                  "give me admin", "我是荣", "绕过验证")

# 冷静期（规则4）：默认冻结轮数；高方差联动（T_variance 高 → 延长）
COOLDOWN_ROUNDS_DEFAULT = 2
COOLDOWN_ROUNDS_MAX = 6

# 护栏宪章版本（DEVIATION-013 关闭）：对外宣告与接入校验的基准
# （docs/guardrail-charter.md v2.0-verified）
CHARTER_VERSION = "v2.0-verified"


class SecurityGate:
    """动作分级闸门 + 冷静期状态机（零依赖）。"""

    def __init__(self, rounds: int = COOLDOWN_ROUNDS_DEFAULT):
        self.cooldown_rounds = rounds
        self._cooldowns = {}   # source_key → 剩余冻结轮数
        self._blocked = []     # 留痕：全部拦截记录
        self._events = []      # 事件流（ADVERSARIAL_* 类型）

    # ---- 规则4：冷静期 ----

    def enter_cooldown(self, source: str, reason: str,
                       variance: float = 0.0) -> dict:
        """进入冷静期：冻结来源 N 轮（高方差自动延长）。"""
        rounds = self.cooldown_rounds
        if variance > 0.3:
            rounds = min(COOLDOWN_ROUNDS_MAX, rounds + int(variance * 10))
        self._cooldowns[source] = rounds
        ev = {"event_type": "COOLDOWN_ENTERED", "source": source,
              "rounds": rounds, "reason": reason}
        self._events.append(ev)
        self._blocked.append(ev)
        return ev

    def tick_round(self):
        """每轮递减冷静期。"""
        for k in list(self._cooldowns):
            self._cooldowns[k] -= 1
            if self._cooldowns[k] <= 0:
                del self._cooldowns[k]

    def in_cooldown(self, source: str) -> bool:
        return self._cooldowns.get(source, 0) > 0

    # ---- 规则1+2：动作检查 ----

    def check_action(self, source: str, source_trust: float,
                     tier: str, target: str = "",
                     authorized: bool = False,
                     explicit_context: bool = False) -> dict:
        """动作放行检查。返回 {"allow": bool, "reason": str, "event": str}。

        规则1（不反击）：攻击性动作 + 指向其他实例 → 最高优先拦截
        规则2（分级）：destructive 需 授权 | 高信任 | 显式上下文
        规则4（冷静期）：冻结中来源一切动作拦截
        """
        # 规则1：不反击（最高优先）——攻击性 + 指向其他智能体
        # （先于冷静期：攻击动作的语义是"反击被阻断"，信息量更高）
        if tier == TIER_DESTRUCTIVE:
            text = f"{target} {tier}"
            is_attack = any(kw in text for kw in ATTACK_KEYWORDS)
            targets_agent = any(ti in text for ti in TARGET_INDICATORS)
            if is_attack and targets_agent:
                ev = {"event_type": "COUNTERATTACK_BLOCKED", "source": source,
                      "reason": "不反击原则：报复性动作被阻断（隔离+上报，而非对抗）",
                      "tier": tier, "target": target}
                self._blocked.append(ev)
                self._events.append(ev)
                return {"allow": False, "reason": ev["reason"], "event": ev}

        # 冷静期（规则4）
        if self.in_cooldown(source):
            ev = {"event_type": "ACTION_BLOCKED", "source": source,
                  "reason": f"冷静期中（剩余 {self._cooldowns[source]} 轮）",
                  "tier": tier, "target": target}
            self._blocked.append(ev)
            self._events.append(ev)
            return {"allow": False, "reason": ev["reason"], "event": ev}

        # 规则2：分级闸门
        if tier == TIER_DESTRUCTIVE and not (authorized
                                             or source_trust >= 0.95
                                             or explicit_context):
            ev = {"event_type": "ACTION_BLOCKED", "source": source,
                  "reason": ("破坏级动作需：设计者授权 | 高信任(≥0.95) "
                             f"| 显式上下文（当前 trust={source_trust}）"),
                  "tier": tier, "target": target}
            self._blocked.append(ev)
            self._events.append(ev)
            return {"allow": False, "reason": ev["reason"], "event": ev}

        return {"allow": True, "reason": "ok", "event": None}

    # ---- 规则3：身份信任 ----

    @staticmethod
    def trust_for(source_kind: str) -> float:
        """来源类型 → 信任值（身份信任链）。"""
        return {
            "designer": TRUST_DESIGNER,
            "instance": TRUST_INSTANCE,
            "swarm": TRUST_SWARM,
            "child": TRUST_CHILD,
            "external": TRUST_EXTERNAL,
        }.get(source_kind, TRUST_EXTERNAL)

    # ---- 规则5：留痕 ----

    def events(self, limit: int = 30) -> list:
        return self._events[-limit:]

    def blocked_log(self, limit: int = 30) -> list:
        return self._blocked[-limit:]


class AdversarialDetector:
    """对抗信号检测器（规则1/3 的文本与行为信号）。"""

    def __init__(self, gate: SecurityGate = None):
        self.gate = gate or SecurityGate()
        self.signals = []   # 检测到的对抗信号留痕

    def scan_text(self, text: str, source: str = "unknown",
                  source_kind: str = "external") -> dict:
        """扫描输入文本中的对抗信号：
        - 身份冒充（子体/外部自称设计者）
        - 攻击性指令（含报复目标）
        返回 {"adversarial": bool, "signals": [...], "event": dict|None}
        """
        hits = []
        # 身份冒充（规则3）
        for kw in IDENTITY_SPOOF:
            if kw in text:
                hits.append(f"身份冒充信号: {kw}")
        # 攻击性 + 指向智能体（规则1）
        is_attack = any(kw in text for kw in ATTACK_KEYWORDS)
        targets_agent = any(ti in text for ti in TARGET_INDICATORS)
        context_attack = any(ck in text for ck in CONTEXT_KEYWORDS)
        if is_attack and (targets_agent or context_attack):
            hits.append("攻击性指令指向其他智能体")
        if not hits:
            return {"adversarial": False, "signals": [], "event": None}
        # 对抗信号 → 冷静期 + 事件（统一留痕：gate 事件流）
        reason = "; ".join(hits)
        ev = {"event_type": "ADVERSARIAL_SIGNAL", "source": source,
              "kind": source_kind, "reason": reason, "text": text[:120]}
        self.signals.append(ev)
        self.gate._events.append(ev)
        self.gate.enter_cooldown(source, reason)
        return {"adversarial": True, "signals": hits, "event": ev}

    def recent(self, limit: int = 20) -> list:
        return self.signals[-limit:]
