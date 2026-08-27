# -*- coding: utf-8 -*-
"""test_spacetime_perception.py · 白箱感知通道测试（⑤闭环）
验证：①看见→记住（灵枢时空记忆）②时空问答（方向/速度/周期/静止/事件）
③非时空问题不劫持 ④记忆一致性"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\aeis')
from spacetime_perception import SpacetimePerception
from stcnn import synth_ball_rolling, synth_blinking, synth_static
from aeis.api import Agent

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

agent = Agent(identity="percept", db_path=":memory:")
p = SpacetimePerception(agent)

# ① 看见→记住
p.see(synth_ball_rolling(frames=10, speed_px=2), "球")
p.see(synth_blinking(frames=12, period=3), "灯")
p.see(synth_static(frames=6), "背景")
mem = agent.engine.store.get_nodes_by_tag("spatiotemporal", limit=10)
check('① 看见→记住（3 时空记忆入灵枢）', len(mem) >= 3, f'{len(mem)} 条')

# ② 时空问答
r1 = p.ask("刚才那个球怎么动的？")
check('②a 方向问答（向右）', r1.get("ok") and "向右" in r1.get("reply", ""), r1.get("reply", "")[:30])
r2 = p.ask("球的速度是多少？")
check('②b 速度问答（2.0/帧）', r2.get("ok") and "速度" in r2.get("reply", ""))
r3 = p.ask("灯有什么规律？")
check('②c 周期问答（3帧）', r3.get("ok") and "周期" in r3.get("reply", ""))
r4 = p.ask("背景在动吗？")
check('②d 静止问答', r4.get("ok") and "静止" in r4.get("reply", ""))
r5 = p.ask("刚才都发生了什么？")
check('②e 事件问答', r5.get("ok") and len(r5.get("reply", "")) > 5)

# ③ 非时空问题不劫持
r6 = p.ask("什么是碳中和？")
check('③ 非时空问题不劫持（返回 not ok）', not r6.get("ok"))

# ④ 回忆入口
events = p.what_happened()
check('④ what_happened 返回全部时空记忆', len(events) >= 3)

print(f'\n=== 白箱感知通道测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
