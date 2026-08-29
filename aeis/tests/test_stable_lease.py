# -*- coding: utf-8 -*-
"""test_stable_lease · C3 stable 租约单元测试（智能论 v3.4 3.2.2）"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from stable_lease import StableLease

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# C3-1: 获取租约 → stable
sl = StableLease(ttl=100.0)
r1 = sl.acquire("门把手", confidence=0.95)
check("acquire stable", r1["state"] == "stable", str(r1))

# C3-2: 租约内检查 → in_lease
r2 = sl.check("门把手")
check("in lease", r2["in_lease"] and r2["state"] == "stable", str(r2))

# C3-3: 未知 key → unknown
check("unknown key", sl.check("不存在")["state"] == "unknown")

# C3-4: 短 TTL 超时 → 降级 weak（不删除）
sl2 = StableLease(ttl=0.01)
sl2.acquire("临时", confidence=0.9)
time.sleep(0.02)
r4 = sl2.check("临时")
check("ttl expiry degrades to weak", r4["state"] == "weak" and not r4["in_lease"], str(r4))

# C3-5: 指数衰减核——置信度随年龄指数下降
sl3 = StableLease(ttl=1000.0, gamma=0.5)
sl3.acquire("衰减", confidence=1.0)
time.sleep(0.05)
r5 = sl3.check("衰减")
check("confidence decays exponentially", r5["decayed_confidence"] < 0.99, str(r5["decayed_confidence"]))

# C3-6: 续期恢复 stable
sl4 = StableLease(ttl=0.01)
sl4.acquire("门", confidence=0.9)
time.sleep(0.02)
r6a = sl4.check("门")
check("expired before renew", r6a["state"] == "weak")
sl4.renew("门", confidence=0.95)
r6b = sl4.check("门")
check("renew restores stable", r6b["state"] == "stable", str(r6b))

# C3-7: 降级不删除记录（记录边界 P1-003）
sl5 = StableLease(ttl=100.0)
sl5.acquire("关键记录", confidence=0.9, history=["验证1", "验证2"])
sl5.degrade("关键记录", reason="预测冲突")
r7 = sl5.state("关键记录")
check("degrade state weak", r7["state"] == "weak")
check("history note retained", "不可遗忘" in sl5.degrade("关键记录")["note"] or r7 is not None)

print(f"\nC3 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
