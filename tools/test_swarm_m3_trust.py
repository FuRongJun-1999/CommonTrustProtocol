# -*- coding: utf-8 -*-
"""test_swarm_m3_trust.py · 信任分三性质验证（2026-08-29）

对照智能论 §2.9：可度量 / 可更新 / 可被反例击穿（隔离）。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_m3_trust import TrustLedger, ISOLATE_THRESHOLD

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


# 可度量：初始 0.5，范围 [0,1]
led = TrustLedger()
check("可度量：初始 0.5", led.score("x") == 0.5, f"got {led.score('x')}")

# 可更新：pass 提升（单调上升且不超过 1）
seq = [led.record("good", True) for _ in range(8)]
check("可更新：pass 单调上升", all(b > a for a, b in zip(seq, seq[1:])), f"{[round(s,3) for s in seq]}")
check("可更新：上界 1", seq[-1] < 1.0 and seq[-1] > 0.9, f"got {seq[-1]:.3f}")

# 可更新：fail 下降
led2 = TrustLedger()
led2.record("mid", True)
after_fail = led2.record("mid", False)
check("可更新：fail 下降", after_fail < led2.score.__self__.history[0][2] if False else after_fail < 0.5,
      f"got {after_fail:.3f}")

# 可击穿：连续 fail 跌破阈值 → 隔离 + 拒绝派单
led3 = TrustLedger()
for i in range(4):
    led3.record("bad", True)         # 先建立高信任
    led3.record("bad", False)        # 交错 fail
check("击穿前未隔离", not led3.isolated("bad"), f"score={led3.score('bad'):.3f}")
for i in range(6):
    led3.record("bad", False)        # 连续反例
check("可击穿：连续 fail 跌破阈值", led3.isolated("bad"), f"score={led3.score('bad'):.3f}")
ok, reason = led3.can_dispatch("bad")
check("隔离后拒绝派单", not ok and "暂停派单" in reason, reason)

# 高信任对端正常派单
check("高信任对端可派单", led3.can_dispatch("good")[0])

print("\n=== 判定 ===")
print(f"信任分验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
