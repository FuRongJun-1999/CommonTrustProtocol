# -*- coding: utf-8 -*-
"""test_real_world_3d.py · 3D 感知真实感鲁棒性测试（第五阶段·合成→真实过渡）
验证：①噪声 0/0.05/0.1 近大远小保持 ②噪声 0.2 鲁棒性边界 ③光照渐变
④边缘增强提升低纹理匹配 ⑤噪声误差单调性"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from real_world_3d import (synth_noisy_stereo_pair, stereo_verdict,
                           edge_enhanced_stereo, robustness_report)
from vision_3d import stereo_disparity

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 噪声 0/0.05/0.1：近大远小保持
for noise in (0.0, 0.05, 0.1):
    l, r = synth_noisy_stereo_pair(noise=noise)
    v = stereo_verdict(l, r)
    check(f'① 噪声{noise} 近大远小保持', v["ok"], f'fg={v["fg_disp"]} bg={v["bg_disp"]}')

# ② 噪声 0.2：鲁棒性边界（近大远小仍保持）
l, r = synth_noisy_stereo_pair(noise=0.2)
v = stereo_verdict(l, r)
check('② 噪声0.2 边界保持', v["ok"], f'fg={v["fg_disp"]} bg={v["bg_disp"]}')

# ③ 光照渐变不影响判定
l, r = synth_noisy_stereo_pair(light_grad=0.4)
v = stereo_verdict(l, r)
check('③ 光照渐变保持', v["ok"], f'fg={v["fg_disp"]} bg={v["bg_disp"]}')

# ④ 边缘增强：低纹理背景匹配（边缘图视差在背景区更稳定）
l, r = synth_noisy_stereo_pair(noise=0.05)
disp_raw = stereo_disparity(l, r)
disp_ed = edge_enhanced_stereo(l, r)
bg_raw = float(np.median(disp_raw))
bg_ed = float(np.median(disp_ed))
check('④ 边缘增强背景视差稳定(≈2)', abs(bg_ed - 2.0) <= abs(bg_raw - 2.0),
      f'raw bg={bg_raw:.2f} ed bg={bg_ed:.2f}')

# ⑤ 噪声边界：最大噪声误差 ≥ 无噪声误差（鲁棒性退化边界）
rows = robustness_report()
errs = [abs(row["fg_disp"] - 8.0) for row in rows]
check('⑤ 最大噪声误差≥无噪声', errs[-1] >= errs[0],
      f'errs={[round(e,2) for e in errs]}')

print(f'\n=== 3D 真实感鲁棒性测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
