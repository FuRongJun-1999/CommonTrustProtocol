# -*- coding: utf-8 -*-
"""test_spatial_qa.py · 3D 时空问答测试（第五阶段·3D 轨迹接入感知记忆）
验证：①看见→记住（灵枢记忆含 3D 运动原语）②3D 问答 5 型 ③记忆自校验 ④静止对照"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\aeis')
from aeis.api import Agent
from spatial_qa import (see_3d_and_remember, ask_3d, verify_3d_remembered)
from spacetime_3d import synth_moving_stereo_frames

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

a = Agent(identity="spatial3d-test", db_path=":memory:")
seq = synth_moving_stereo_frames(frames=10, speed_px=2, direction="right")
motion, node = see_3d_and_remember(a, seq, "球")
seq_s = synth_moving_stereo_frames(frames=6, speed_px=0, direction="right")
motion_s, node_s = see_3d_and_remember(a, seq_s, "背景")

# ① 看见→记住：记忆含方向 x+/速度/位移/一致性
c = node.content or ""
check('①a 记忆含方向 x+', "方向=x+" in c, c[:50])
check('①b 记忆含速度', "速度=" in c and "位移=" in c and "一致性=" in c, c[:50])
check('①c 静止对照进记忆', "静止" in (node_s.content or ""), (node_s.content or "")[:40])

# ② 3D 问答 5 型
r = ask_3d(a, "刚才那个球往哪飞了？")
check('②a 方向问答', r.get("ok") and "x+" in r.get("reply", ""), r.get("reply", ""))
r = ask_3d(a, "球飞多快？")
check('②b 速度问答', r.get("ok") and "速度" in r.get("reply", ""), r.get("reply", ""))
r = ask_3d(a, "球飞了多远？")
check('②c 距离问答', r.get("ok") and "位移" in r.get("reply", ""), r.get("reply", ""))
r = ask_3d(a, "球的轨迹直吗？")
check('②d 轨迹问答', r.get("ok") and "一致性" in r.get("reply", ""), r.get("reply", ""))
r = ask_3d(a, "背景在动吗？")
check('②e 静止问答', r.get("ok") and "静止" in r.get("reply", ""), r.get("reply", ""))

# ③ 记忆自校验
ok1, _ = verify_3d_remembered(a, node, motion)
ok2, _ = verify_3d_remembered(a, node_s, motion_s)
check('③a 球记忆一致', ok1, '')
check('③b 背景记忆一致', ok2, '')

# ④ 非 3D 问题回落
r = ask_3d(a, "什么是碳中和？")
check('④ 非 3D 问题回落', not r.get("ok") and r.get("type") is None, r.get("reply", ""))

print(f'\n=== 3D 时空问答测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
