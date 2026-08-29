# -*- coding: utf-8 -*-
"""test_channel_credibility · B1 通道可信度单元测试（智能论 v3.4 2.9.1a）"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from channel_credibility import ChannelCredibilityRegistry, DEFAULT_CHANNELS

passed = failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# 1. 初始状态：全通道 Beta(2,2) 先验 → credibility=0.5
reg = ChannelCredibilityRegistry()
check("init 6 channels", len(reg.registry()) == 6, str(len(reg.registry())))
check("init credibility 0.5", all(abs(reg.credibility(c) - 0.5) < 1e-6 for c in DEFAULT_CHANNELS))

# 2. 命中提升可信度
reg.record_hit("visual", conf=1.0, strong=False)
c1 = reg.credibility("visual")
check("hit raises credibility", c1 > 0.5, str(c1))

# 3. 未命中降低可信度
reg.record_miss("visual", conf=1.0, strong=False)
c2 = reg.credibility("visual")
check("miss lowers credibility", c2 < c1, f"{c2} vs {c1}")

# 4. 强验证比弱验证更新更快（同样命中，可信度变化更大）
reg2 = ChannelCredibilityRegistry()
reg2.record_hit("action", conf=1.0, strong=True)
reg3 = ChannelCredibilityRegistry()
reg3.record_hit("action", conf=1.0, strong=False)
check("strong faster than weak", reg2.credibility("action") > reg3.credibility("action"),
      f"{reg2.credibility('action')} vs {reg3.credibility('action')}")

# 5. 高置信命中比低置信命中提升更多
reg4 = ChannelCredibilityRegistry()
reg4.record_hit("search", conf=1.0, strong=False)
reg5 = ChannelCredibilityRegistry()
reg5.record_hit("search", conf=0.3, strong=False)
check("high conf > low conf", reg4.credibility("search") > reg5.credibility("search"))

# 6. 持久化
with tempfile.TemporaryDirectory() as td:
    p = os.path.join(td, "cred.json")
    r6 = ChannelCredibilityRegistry(persist_path=p)
    r6.record_hit("visual", conf=0.9, strong=True)
    r6.save()
    r7 = ChannelCredibilityRegistry(persist_path=p)
    check("persist roundtrip", abs(r7.credibility("visual") - r6.credibility("visual")) < 1e-6)

# 7. 降权/检修状态
reg8 = ChannelCredibilityRegistry()
for _ in range(200):
    reg8.record_miss("audio", conf=1.0, strong=True)
st = reg8.channel_state("audio")
check("maintenance status at low cred", st["status"] == "maintenance", st["status"])

print(f"\nB1 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
