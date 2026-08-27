# -*- coding: utf-8 -*-
"""test_image_processing.py · 图像处理基线测试（第四阶段）
验证：①灰度化 ②Sobel 边缘（方块边界 recall）③块匹配光流（方向/位移）
④静态不误报（帧差显著性）⑤边缘方向"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from image_processing import (grayscale, sobel, optical_flow_block,
                              motion_summary, edges_accuracy)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# 合成：渐变背景 + 方块
H = W = 64
bg = np.zeros((H, W), dtype=np.float32)
for i in range(H):
    bg[i, :] = i / H
img1 = bg.copy()
img1[20:36, 10:26] = 0.9
gt = np.zeros((H, W), dtype=np.float32)
gt[20, 10:26] = gt[35, 10:26] = 1
gt[20:36, 10] = gt[20:36, 25] = 1

# ① 灰度化（RGB 合成）
rgb = np.stack([img1 * 255] * 3, axis=-1).astype(np.uint8)
g = grayscale(rgb)
check('① 灰度化（RGB→灰度）', abs(g[30, 30] - img1[30, 30] * 255) < 10)

# ② Sobel 边缘
mag, ang = sobel(img1)
acc = edges_accuracy(mag, gt)
check('②a 边缘 recall（真边缘全检出）', acc['recall'] >= 0.9, f"{acc['recall']}")
check('②b 边缘 F1 基线', acc['f1'] >= 0.5, f"{acc['f1']}")
# 边缘方向：上边界的 Gy 应负（亮度从上往下增 → 上边界向暗侧）
up_ang = ang[20, 18]
check('②c 边缘方向计算（上边界角≈90°）', 60 <= abs(up_ang) <= 120, f"{up_ang:.1f}°")

# ③ 光流（方块右移 3px）
img2 = bg.copy()
img2[20:36, 13:29] = 0.9
fy, fx, sig = optical_flow_block(img1, img2, block=8, search=5)
ms = motion_summary(fy, fx, sig)
check('③a 光流方向=向右', ms['direction'] == '向右', ms['direction'])
check('③b 光流位移≈3px', abs(ms['speed'] - 3.0) < 1.0, f"{ms['speed']}")
check('③c 运动块数>0', ms['active_blocks'] > 0)

# ④ 静态不误报
fy0, fx0, sig0 = optical_flow_block(img1, img1, block=8, search=5)
ms0 = motion_summary(fy0, fx0, sig0)
check('④ 静态不误报（帧差显著性过滤）', not ms0['moving'] and ms0['direction'] == '静止')

print(f'\n=== 图像处理基线测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
