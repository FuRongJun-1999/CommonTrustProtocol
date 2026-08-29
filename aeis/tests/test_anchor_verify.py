# -*- coding: utf-8 -*-
"""test_anchor_verify · 里程碑1.4 多感知机锚点验证单元测试"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.anchor_verify import AnchorVerification, STRONG_CHANNELS, WEAK_CHANNELS

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

av = AnchorVerification()

# 1. 通道强弱分类
check("tactile is strong", "tactile" in STRONG_CHANNELS)
check("action is strong", "action" in STRONG_CHANNELS)
check("audio is strong", "audio" in STRONG_CHANNELS)
check("visual is weak", "visual" in WEAK_CHANNELS)
check("graph is weak", "graph" in WEAK_CHANNELS)

# 2. 仅视觉（弱验证）→ ACCEPT_weak（疑似）
av.add_channel_evidence("chair_1", "visual", 0.8)
r1 = av.verify_anchor("chair_1")
check("visual only = weak", r1["confirmation"] == "ACCEPT_weak", str(r1["confirmation"]))

# 3. 视觉 + 触觉（强验证）→ ACCEPT_strong
av.add_channel_evidence("chair_1", "tactile", 0.8)
r2 = av.verify_anchor("chair_1")
check("visual+tactile = strong", r2["confirmation"] == "ACCEPT_strong", str(r2["confirmation"]))

# 4. 多次稳定 → ACCEPT_stable
for _ in range(3):
    r3 = av.verify_anchor("chair_1")
check("stable rounds -> ACCEPT_stable", r3["confirmation"] == "ACCEPT_stable", str(r3["confirmation"]))

# 5. 多通道协同（视觉+触觉+听觉+行动）
av2 = AnchorVerification()
av2.add_channel_evidence("table_1", "visual", 0.9)
av2.add_channel_evidence("table_1", "tactile", 0.85)
av2.add_channel_evidence("table_1", "audio", 0.7)
av2.add_channel_evidence("table_1", "action", 0.95)
r4 = av2.verify_anchor("table_1")
check("multi-channel strong", r4["confirmation"] in ("ACCEPT_strong", "ACCEPT_stable"), r4["confirmation"])
check("4 channels recorded", len(r4["channel_evidence"]) == 4)

# 6. 矛盾检测：视觉说椅子，触觉说箱子 → 冲突
av3 = AnchorVerification()
av3.add_channel_evidence("obj_1", "visual", 0.9)
av3.add_channel_evidence("obj_1", "tactile", 0.8)
conf = av3.channel_conflict_detect("obj_1", "tactile", "椅子", "箱子")
check("conflict detected", conf["conflict_detected"] and conf["conflict_count"] == 1, str(conf))
r5 = av3.verify_anchor("obj_1")
check("conflict blocks strong", r5["confirmation"] == "ACCEPT_weak", str(r5["confirmation"]))

# 7. 无证据 → weak
r6 = av.verify_anchor("nonexistent_anchor")
check("no evidence weak", r6.get("confirmation") == "ACCEPT_weak" or r6.get("error") is not None, str(r6))

# 8. 摘要
summ = av.verification_summary()
check("summary has anchors", "chair_1" in summ)

print(f"\nAVERIFY result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
