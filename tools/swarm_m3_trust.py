# Copyright 2026 灵枢 (Lingshu) · MIT
"""swarm_m3_trust.py · M3 预备——节点信任分（2026-08-29 心跳）

蓝图映射表命题工程化：**信任 = 协作者行为在可接受偏差内保持稳定的置信概率**
（智能论 §2.9）。三条性质对齐理论：
- 可度量：P_trust ∈ [0,1]，每对端一个分值
- 可更新：行为验证后更新（指数滑动：pass 提升、fail 下降）
- 可被反例击穿：连续 fail 使信任跌破隔离阈值 → 拒绝派单（分工由信任决定）
"""

from __future__ import annotations


ISOLATE_THRESHOLD = 0.3   # 低于此值 → 隔离（不再派 TASK，与荣 08-18 噪音隔离决策同构）
ALPHA = 0.3               # 更新步长（响应速度 vs 稳定性的折中）


class TrustLedger:
    """对端信任账本：score(peer) 查询 / record(peer, ok) 更新 / isolated 判定。"""

    def __init__(self, initial: float = 0.5):
        self.initial = initial
        self.scores: dict[str, float] = {}
        self.history: list[tuple[str, bool, float]] = []  # (peer, pass, 更新后分值)

    def score(self, peer: str) -> float:
        return self.scores.get(peer, self.initial)

    def isolated(self, peer: str) -> bool:
        return self.score(peer) < ISOLATE_THRESHOLD

    def record(self, peer: str, ok: bool) -> float:
        """行为验证后更新信任（可更新性；连续 fail=反例击穿）。"""
        t = self.score(peer)
        t = t + ALPHA * ((1.0 - t) if ok else -t)
        t = max(0.0, min(1.0, t))
        self.scores[peer] = t
        self.history.append((peer, ok, t))
        return t

    def can_dispatch(self, peer: str) -> tuple[bool, str]:
        """分工前置检查：隔离中的对端拒绝派单（信任决定分工）。"""
        if self.isolated(peer):
            return False, (f"对端 {peer} 信任分 {self.score(peer):.2f} "
                           f"低于隔离阈值 {ISOLATE_THRESHOLD}——暂停派单")
        return True, f"信任分 {self.score(peer):.2f}"


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    led = TrustLedger()
    for i in range(5):
        led.record("nodeB", True)
    print("连续 5 次 pass 后:", round(led.score("nodeB"), 3))
    for i in range(6):
        led.record("nodeB", False)
    print("连续 6 次 fail 后:", round(led.score("nodeB"), 3),
          "| isolated:", led.isolated("nodeB"))
    print("派单检查:", led.can_dispatch("nodeB"))
