# -*- coding: utf-8 -*-
"""test_confirmation · B3 完全确认 + B4 Value 双层结构单元测试（智能论 v3.4 2.9.3a + 5.3）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from confirmation import (ConfirmationEvaluator, gain_task, kl_binary, value)

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# B3-1: 完全确认四条件全满足 → confirmed + ACCEPT_stable
ev = ConfirmationEvaluator()
res = ev.evaluate({"visual": 0.9, "action": 0.8}, realized_kl=0.3, stable_rounds=10)
check("confirmed when all conditions", res["confirmed"], str(res))
check("tier stable", res["tier"] == "ACCEPT_stable", res["tier"])

# B3-2: 无强验证 → ACCEPT_weak（疑似确认）
res2 = ev.evaluate({"visual": 0.9}, realized_kl=0.0, stable_rounds=0)
check("weak without strong verification", res2["tier"] == "ACCEPT_weak", res2["tier"])
check("not confirmed weak", not res2["confirmed"])

# B3-3: 有强验证但无稳定 → ACCEPT_strong
res3 = ev.evaluate({"visual": 0.9}, realized_kl=0.2, stable_rounds=1)
check("strong without stability", res3["tier"] == "ACCEPT_strong", res3["tier"])

# B3-4: 通道不达标 → NOT_ACCEPTED
res4 = ev.evaluate({"visual": 0.1}, realized_kl=0.5, stable_rounds=10)
check("not accepted when channel fails", res4["tier"] == "NOT_ACCEPTED", res4["tier"])

# B3-5: 内部矛盾 → 不确认
res5 = ev.evaluate({"visual": 0.9, "action": 0.8}, realized_kl=0.3, stable_rounds=10, contradiction=True)
check("contradiction blocks confirmation", not res5["confirmed"])

# B4-1: kl_binary——信念不变 → 0（自我应答出局）
check("KL zero when no change", abs(kl_binary(0.5, 0.5)) < 1e-9)
check("KL positive on change", kl_binary(0.8, 0.5) > 0)

# B4-2: gain_task——无关任务（relevance=0）→ 0（无目的猎奇出局）
check("gain zero for irrelevant", gain_task(0.8, 0.5, task_relevance=0.0) == 0.0)
check("gain positive for relevant", gain_task(0.8, 0.5, task_relevance=1.0) > 0)

# B4-3: value——低 Gain 被 σ 门控压制
v_low = value(s_delta_d=10.0, gain=0.0)
v_high = value(s_delta_d=10.0, gain=0.5)
check("low gain suppressed", v_low < 0.01, str(v_low))
check("high gain passes", v_high > 1.0, str(v_high))

# B4-4: value——ΔD=0 → 0（不缩小信息差则无价值）
check("zero deltaD zero value", abs(value(0.0, 0.5)) < 1e-9)

print(f"\nB3+B4 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
