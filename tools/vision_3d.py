# -*- coding: utf-8 -*-
"""vision_3d.py · 白箱自身 3D 视觉（第四阶段·感知→3D 重建）
立体视差：双目图像 → 块匹配视差 → 深度 Z=f·B/d → 3D 点云
衔接灵枢 WORLD3D（语义→3D 反投影）的反向：感知（图像）→ 3D 结构。
零依赖 numpy 确定性实现（D-005）。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')


def stereo_disparity(left, right, block=8, search=16):
    """立体视差：左图每块在右图搜索窗内找最小 SAD 匹配 → 视差图
    视差 d = 左块列 - 右匹配列（越大 = 物体越近）"""
    L = np.asarray(left, dtype=np.float32)
    R = np.asarray(right, dtype=np.float32)
    H, W = L.shape
    disp = np.zeros((H // block, W // block), dtype=np.float32)
    for bi in range(0, H - block + 1, block):
        for bj in range(0, W - block + 1, block):
            ref = L[bi:bi + block, bj:bj + block]
            best_sad, best_d = 1e18, 0.0
            for d in range(0, search + 1):
                xj = bj - d
                if xj < 0 or xj + block > W:
                    break
                cand = R[bi:bi + block, xj:xj + block]
                sad = float(np.abs(ref - cand).sum())
                if sad < best_sad:
                    best_sad, best_d = sad, d
            disp[bi // block, bj // block] = best_d
    return disp


def depth_from_disparity(disp, focal=100.0, baseline=1.0):
    """视差 → 深度：Z = f·B/d（f 焦距像素，B 基线，d 视差）"""
    d = np.asarray(disp, dtype=np.float32)
    d_safe = np.where(d > 0.5, d, 0.5)  # 极小视差保护
    return (focal * baseline) / d_safe


def pointcloud_from_depth(depth, block=8):
    """深度图 → 3D 点云：(x, y, z)——感知→3D 重建的输出"""
    H, W = depth.shape
    pts = []
    for i in range(H):
        for j in range(W):
            z = float(depth[i, j])
            if z > 1e4:
                continue
            x = (j * block + block / 2) / 10.0  # 像素 → 世界尺度
            y = (i * block + block / 2) / 10.0
            pts.append((round(x, 2), round(y, 2), round(z, 2)))
    return pts


def synth_stereo_pair(size=64, fg_rows=(20, 36), fg_left=(10, 26), disp_fg=8,
                      disp_bg=2):
    """合成双目：前景方块（视差大=近）+ 背景纹理（视差小=远）
    左图方块在 fg_left；右图方块左移 disp_fg（视差）"""
    H = W = size
    rng = np.random.RandomState(0)
    bg = rng.rand(H, W).astype(np.float32) * 0.4  # 背景纹理（块匹配需要纹理）
    left = bg.copy()
    right = bg.copy()
    # 背景视差：右图 = 左图背景左移 disp_bg
    right[:, :W - disp_bg] = left[:, disp_bg:]
    # 前景方块：左图在 fg_left，右图左移 disp_fg（更近 → 视差更大）
    r0, r1 = fg_rows
    c0, c1 = fg_left
    left[r0:r1, c0:c1] = 0.9
    right[r0:r1, c0 - disp_fg:c1 - disp_fg] = 0.9
    return left, right


if __name__ == "__main__":
    print("=== 白箱自身 3D 视觉：立体视差 → 深度 → 3D 点云（零 LLM）===\n")

    left, right = synth_stereo_pair()
    print("① 合成双目图像（前景方块近 + 背景纹理远）")

    disp = stereo_disparity(left, right, block=8, search=16)
    depth = depth_from_disparity(disp)
    print("② 立体视差图（块匹配 SAD）")
    # 方块区域（前景）视差应大
    fg_blocks = (slice(20 // 8, 36 // 8), slice(10 // 8, 26 // 8))
    fg_disp = float(disp[fg_blocks].mean())
    bg_disp = float(np.median(disp))  # 背景视差众数
    print(f"   前景视差={fg_disp:.1f} 背景视差≈{bg_disp:.1f}（前景大=近）")

    print("\n③ 深度：Z = f·B/d（前景近 Z 小，背景远 Z 大）")
    fg_depth = float(depth[fg_blocks].mean())
    bg_depth = float(np.median(depth))
    print(f"   前景深度={fg_depth:.1f} 背景深度={bg_depth:.1f}")

    print("\n④ 3D 点云（感知→3D 重建输出）")
    pts = pointcloud_from_depth(depth, block=8)
    near = [p for p in pts if p[2] < 50]
    far = [p for p in pts if p[2] >= 50]
    print(f"   近点（前景方块）: {len(near)} 个 | 远点（背景）: {len(far)} 个")
    if near:
        x0 = min(p[0] for p in near)
        x1 = max(p[0] for p in near)
        print(f"   前景点云 x 范围: [{x0:.1f}, {x1:.1f}]（对应方块位置）")

    ok = fg_disp > bg_disp and fg_depth < bg_depth and len(near) > 0
    print(f"\n=== 判定 ===\n感知→3D（视差→深度→点云）: "
          f"{'✔ 成立（前景近/背景远，3D 结构重建）' if ok else '✘'}")
