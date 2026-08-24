# -*- coding: utf-8 -*-
"""test_3d_in_chat.py · 3D 感知进 chat_engine 主路由（第五阶段·3D 时空问答接入）
验证：①3D 问题自动走感知通道（perception=True）②3D 距离/轨迹问答 ③非 3D 不劫持
④无 3D 记忆时诚实回落主流程"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
sys.path.insert(0, CTP + r'\tools')
sys.path.insert(0, CTP + r'\aeis')
import wisdom.chat_engine as ce
sys.path.insert(0, CTP + r'\tools')
from aeis.api import Agent
from spatial_qa import see_3d_and_remember, ask_3d
from spacetime_3d import synth_moving_stereo_frames

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

agent = Agent(identity="phase5-3d-chat", db_path=":memory:")
seq = synth_moving_stereo_frames(frames=10, speed_px=2, direction="right")
see_3d_and_remember(agent, seq, "球")
perceiver = lambda q: ask_3d(agent, q)

# ① 3D 问题自动走感知通道
r1 = ce.chat(dex=None, message="刚才那个球往哪飞了？", perceiver_fn=perceiver)
check('①a 3D 方向问题走感知', r1.get("perception") and "x+" in r1.get("reply", ""),
      r1.get("reply", "")[:30])
r2 = ce.chat(dex=None, message="球飞了多远？", perceiver_fn=perceiver)
check('①b 3D 距离问题走感知', r2.get("perception") and "位移" in r2.get("reply", ""),
      r2.get("reply", "")[:30])
r3 = ce.chat(dex=None, message="球的轨迹直吗？", perceiver_fn=perceiver)
check('①c 3D 轨迹问题走感知', r3.get("perception") and "一致性" in r3.get("reply", ""),
      r3.get("reply", "")[:30])

# ② 非 3D 问题不劫持（正常走主流程）
r4 = ce.chat(dex=None, message="你好呀", perceiver_fn=perceiver)
check('② 非 3D 问题不劫持', not r4.get("perception"))

# ③ 无 3D 记忆时诚实回落（感知器 ok=False → 主流程正常应答）
agent2 = Agent(identity="phase5-3d-empty", db_path=":memory:")
perceiver2 = lambda q: ask_3d(agent2, q)
r5 = ce.chat(dex=None, message="球往哪飞了？", perceiver_fn=perceiver2)
check('③ 无记忆诚实回落', not r5.get("perception") and r5.get("reply", ""),
      r5.get("reply", "")[:36])

print(f'\n=== 3D 感知进主路由测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
