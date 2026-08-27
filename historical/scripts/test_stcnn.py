# -*- coding: utf-8 -*-
"""test_stcnn.py · 3D 时空 CNN 原型测试（白箱自举第三阶段·多模态主线）
验证：①时空体素化+3D卷积 ②时空原语（方向/速度/周期/静止基线）
③周期检测边界（非周期→None） ④时空记忆图（记住/回忆/一致性/查询）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from stcnn import (frames_to_voxel, conv3d, MOTION_KERNEL,
                   extract_spatiotemporal_primitives, SpatiotemporalMemory,
                   synth_ball_rolling, synth_static, synth_blinking,
                   detect_period)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 体素化 + 3D 卷积
frames = synth_ball_rolling(frames=8, size=24)
vox = frames_to_voxel(frames)
check('①a 体素化 (T,H,W)', vox.shape == (8, 24, 24), str(vox.shape))
feat = conv3d(vox, MOTION_KERNEL)
check('①b 3D 卷积输出时空特征图', feat.shape == (7, 22, 22), str(feat.shape))
check('①c 运动核有响应（非零特征）', abs(feat).sum() > 0)

# ② 时空原语
p1, _ = extract_spatiotemporal_primitives(synth_ball_rolling(frames=10, speed_px=2))
check('②a 方向=向右', p1['direction'] == '向右', p1['direction'])
check('②b 速度≈2/帧', abs(p1['speed'] - 2.0) < 0.5, str(p1['speed']))
check('②c 运动中', p1['moving'] is True)
p2, _ = extract_spatiotemporal_primitives(synth_blinking(frames=12, period=3))
check('②d 周期=3帧', p2['period'] == 3, str(p2['period']))
p3, _ = extract_spatiotemporal_primitives(synth_static(frames=6))
check('②e 静止基线（不动）', p3['moving'] is False and p3['direction'] == '静止')

# ③ 周期检测边界
check('③a 无重复间隔信号 → None（非周期）', detect_period([0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0]) is None)
check('③b 常亮无信号 → None', detect_period([0, 0, 0, 0]) is None)

# ④ 时空记忆图
mem = SpatiotemporalMemory()
mem.remember(p1, label='球')
mem.remember(p2, label='灯')
mem.remember(p3, label='背景')
check('④a 记住 3 个事件', len(mem.events) == 3)
check('④b 回忆[球]方向向右', mem.recall({'label': '球'})[0]['direction'] == '向右')
check('④c 回忆[运动中]', len(mem.recall({'moving': True})) == 2)
check('④d 回忆[周期3]（灯）', len(mem.recall({'period': 3})) == 1)
check('④e 一致性自校验（无幻觉）', mem.verify_consistency() is True)

print(f'\n=== 3D 时空 CNN 测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
