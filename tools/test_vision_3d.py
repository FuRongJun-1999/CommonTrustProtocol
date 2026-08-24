# -*- coding: utf-8 -*-
"""test_vision_3d.py · 3D 视觉测试（第四阶段·感知→3D）
验证：①立体视差（前景视差大=近）②深度（近小远大）③3D 点云重建
④相同图像视差=0（无立体不重建）"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from vision_3d import (stereo_disparity, depth_from_disparity,
                       pointcloud_from_depth, synth_stereo_pair)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

left, right = synth_stereo_pair()
disp = stereo_disparity(left, right, block=8, search=16)
depth = depth_from_disparity(disp)

fg = (slice(20 // 8, 36 // 8), slice(10 // 8, 26 // 8))
fg_disp = float(disp[fg].mean())
bg_disp = float(np.median(disp))
fg_depth = float(depth[fg].mean())
bg_depth = float(np.median(depth))

check('① 前景视差 > 背景（近大远小）', fg_disp > bg_disp,
      f'{fg_disp:.1f} vs {bg_disp:.1f}')
check('② 前景深度 < 背景（近小远大）', fg_depth < bg_depth,
      f'{fg_depth:.1f} vs {bg_depth:.1f}')
pts = pointcloud_from_depth(depth, block=8)
near = [p for p in pts if p[2] < 50]
check('③ 3D 点云重建（近点+远点）', len(near) > 0 and len(pts) > len(near),
      f'{len(near)} 近点 / {len(pts)} 总点')

# ④ 相同图像 → 视差 0（无立体信息）
disp0 = stereo_disparity(left, left, block=8, search=16)
check('④ 相同图像视差=0（无立体不重建）', float(disp0.max()) < 0.5,
      f'max={float(disp0.max()):.2f}')

print(f'\n=== 3D 视觉测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
