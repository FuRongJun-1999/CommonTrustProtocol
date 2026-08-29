# -*- coding: utf-8 -*-
"""test_accept_tiers · C4 ACCEPT 确认度分层单元测试（智能论 v3.4 三·正交化）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from confirmation import ConfirmationEvaluator

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

ev = ConfirmationEvaluator(conf_threshold=0.5, kl_threshold=0.05, stable_rounds=5)

# C4-1: ACCEPT_weak——通道一致但无独立验证（疑似确认 → 不直答）
r1 = ev.evaluate({"visual": 0.9}, realized_kl=0.0, stable_rounds=0)
check("weak = channels only", r1["tier"] == "ACCEPT_weak", r1["tier"])
check("weak not confirmed", not r1["confirmed"])

# C4-2: ACCEPT_strong——独立验证命中（正常直答）
r2 = ev.evaluate({"visual": 0.9}, realized_kl=0.3, stable_rounds=2)
check("strong = channels+verification", r2["tier"] == "ACCEPT_strong", r2["tier"])

# C4-3: ACCEPT_stable——跨时间稳定（直答+知识强化）
r3 = ev.evaluate({"visual": 0.9, "action": 0.8}, realized_kl=0.3, stable_rounds=10)
check("stable = channels+verification+stability", r3["tier"] == "ACCEPT_stable", r3["tier"])
check("stable confirmed", r3["confirmed"])

# C4-4: DEFER 语义——通道一致但验证路径未完成 = ACCEPT_weak 特例
# （感知一致但验证未完成 → 标记"待验证"）
r4 = ev.evaluate({"visual": 0.8, "action": 0.6}, realized_kl=0.0, stable_rounds=0)
check("defer-like = weak (verification pending)", r4["tier"] == "ACCEPT_weak", r4["tier"])

# C4-5: REJECT/BLINDSPOT 不参与确认度分层（通道不达标 → NOT_ACCEPTED）
r5 = ev.evaluate({"visual": 0.1}, realized_kl=0.5, stable_rounds=10)
check("not accepted = no tier", r5["tier"] == "NOT_ACCEPTED", r5["tier"])

# C4-6: 正交性——资格(ACCEPT)与确认度(weak/strong/stable)正交
# ACCEPT 资格满足（通道达标）但确认度可分层
check("qualification orthogonal to tier",
      r2["tier"] == "ACCEPT_strong" and r3["tier"] == "ACCEPT_stable" and r1["tier"] == "ACCEPT_weak")

print(f"\nC4 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
