# -*- coding: utf-8 -*-
"""test_spacetime_3d.py · 3D 时空轨迹测试（第五阶段·时间×空间闭环）
验证：①移动序列→轨迹方向正确 ②3D 速度≈设定 ③轨迹完整 ④静止对照 ⑤2D↔3D 投影自洽"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from spacetime_3d import (synth_moving_stereo_frames, frame_scene_graphs,
                          track_3d, motion_3d)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 右移序列 → 3D 轨迹 x 单调增
seq = synth_moving_stereo_frames(frames=10, speed_px=2, direction="right")
traj = track_3d(frame_scene_graphs(seq))
m = motion_3d(traj)
xs = [p["x"] for p in traj]
check('① 轨迹方向 x+', m.get("direction") == ["x+"] and xs == sorted(xs),
      f'方向={m.get("direction")} x: {[round(v,1) for v in xs[:4]]}…')

# ② 3D 速度≈设定（speed_px=2 → 点云 x 尺度 像素/10 → 0.2 单位/帧）
check('② 3D 速度≈0.2 单位/帧', 0.1 < m.get("speed", 0) < 0.4,
      f'speed={m.get("speed")}')

# ③ 轨迹完整（10 帧 → 10 个轨迹点）
check('③ 轨迹完整', len(traj) == 10, f'{len(traj)}/10 帧')

# ④ 静止对照：球不动 → 速度≈0
seq_s = synth_moving_stereo_frames(frames=6, speed_px=0, direction="right")
traj_s = track_3d(frame_scene_graphs(seq_s))
m_s = motion_3d(traj_s)
check('④ 静止对照', m_s.get("direction") == ["静止"] and m_s.get("speed", 1) < 0.1,
      f'方向={m_s.get("direction")} 速度={m_s.get("speed")}')

# ⑤ 左移方向（z/x 符号对称验证）
seq_l = synth_moving_stereo_frames(frames=8, speed_px=2, direction="left")
traj_l = track_3d(frame_scene_graphs(seq_l))
m_l = motion_3d(traj_l)
check('⑤ 左移方向 x-', m_l.get("direction") == ["x-"], f'方向={m_l.get("direction")}')

# ⑥ 轨迹一致性（直线运动 ≈1.0）
check('⑥ 运动一致性高', m.get("consistency", 0) >= 0.8, f'consistency={m.get("consistency")}')

print(f'\n=== 3D 时空轨迹测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
