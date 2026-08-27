# -*- coding: utf-8 -*-
"""test_multimodal_bridge.py · 多模态对接测试（3D 时空 CNN × 灵枢记忆）
验证：①看见→时空原语（方向/速度/周期）②记住→灵枢记忆写入
③回忆→灵枢 recall 命中 ④一致性自校验 ⑤边界（无运动帧）"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\aeis')
from multimodal_bridge import (see_and_remember, recall_event,
                               verify_remembered)
from stcnn import (synth_ball_rolling, synth_blinking, synth_static,
                   extract_spatiotemporal_primitives)
from aeis.api import Agent

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

agent = Agent(identity="multi-bridge", db_path=":memory:")

# ① 看见→时空原语
p1, _ = extract_spatiotemporal_primitives(synth_ball_rolling(frames=10, speed_px=2))
check('①a 球方向=向右', p1['direction'] == '向右', p1['direction'])
check('①b 球速度≈2/帧', abs(p1['speed'] - 2.0) < 0.5)
p2, _ = extract_spatiotemporal_primitives(synth_blinking(frames=12, period=3))
check('①c 灯周期=3帧', p2['period'] == 3, str(p2['period']))
p3, _ = extract_spatiotemporal_primitives(synth_static(frames=6))
check('①d 背景静止', not p3['moving'])

# ② 看见→记住→灵枢记忆
_, n1 = see_and_remember(agent, synth_ball_rolling(frames=10, speed_px=2), "球")
_, n2 = see_and_remember(agent, synth_blinking(frames=12, period=3), "灯")
_, n3 = see_and_remember(agent, synth_static(frames=6), "背景")
mem = agent.engine.store.get_nodes_by_tag("spatiotemporal", limit=10)
check('② 3 场景全部写入灵枢记忆', len(mem) >= 3, f"{len(mem)} 条")

# ③ 回忆命中
h1 = recall_event(agent, "球 运动", limit=2)
check('③a 召回「球」', bool(h1) and "球" in h1[0][0].content)
h2 = recall_event(agent, "灯 周期", limit=2)
check('③b 召回「灯」', bool(h2) and "灯" in h2[0][0].content and "周期" in h2[0][0].content)

# ④ 记住一致性
ok1, _ = verify_remembered(agent, n1, p1)
ok2, _ = verify_remembered(agent, n2, p2)
check('④ 记住一致性（原语↔记忆无幻觉）', ok1 and ok2)

# ⑤ 边界：无运动全黑帧
import numpy as np
black = [np.zeros((16, 16), dtype=np.float32) for _ in range(5)]
pb, _ = extract_spatiotemporal_primitives(black)
check('⑤ 全黑帧 → 无运动', not pb['moving'] and pb['motion_magnitude'] == 0.0)

print(f'\n=== 多模态对接测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
