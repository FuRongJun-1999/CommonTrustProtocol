# -*- coding: utf-8 -*-
"""image_processing.py · 白箱图像处理算法（第四阶段·真实图像→时空原语）
从合成帧到真实图像：灰度化 → Sobel 边缘 → 块匹配光流 → 运动摘要
衔接 stcnn：真实图像序列经本层预处理 → 时空原语（stcnn 现有方向/速度/周期）。
零依赖 numpy 确定性实现（D-005）。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')


def grayscale(img):
    """RGB(...,3) 或灰度 → 灰度 0-255 float"""
    arr = np.asarray(img, dtype=np.float32)
    if arr.ndim == 3 and arr.shape[-1] >= 3:
        r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
        return 0.299 * r + 0.587 * g + 0.114 * b
    return arr


def sobel(gray):
    """Sobel 边缘检测：Gx, Gy → 梯度幅值 + 方向（度）"""
    g = np.asarray(gray, dtype=np.float32)
    H, W = g.shape
    Gx = np.zeros_like(g)
    Gy = np.zeros_like(g)
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    Ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
    for i in range(1, H - 1):
        for j in range(1, W - 1):
            patch = g[i - 1:i + 2, j - 1:j + 2]
            Gx[i, j] = float((patch * Kx).sum())
            Gy[i, j] = float((patch * Ky).sum())
    mag = np.sqrt(Gx ** 2 + Gy ** 2)
    ang = np.degrees(np.arctan2(Gy, Gx + 1e-9))
    return mag, ang


def optical_flow_block(frame1, frame2, block=8, search=4):
    """块匹配光流：每块在第二帧搜索窗内找最相似块（SAD 最小）
    返回 (flow_y, flow_x, sig)：sig = 每块帧差显著性（|f1-f2| 块均值——
    真实运动块显著，静止/渐变块近 0——防静态误报）"""
    f1 = np.asarray(frame1, dtype=np.float32)
    f2 = np.asarray(frame2, dtype=np.float32)
    H, W = f1.shape
    flow_y = np.zeros((H // block, W // block), dtype=np.float32)
    flow_x = np.zeros((H // block, W // block), dtype=np.float32)
    sig = np.zeros((H // block, W // block), dtype=np.float32)
    for bi in range(0, H - block + 1, block):
        for bj in range(0, W - block + 1, block):
            ref = f1[bi:bi + block, bj:bj + block]
            # 帧差显著性（该块在帧间是否变化）
            sig[bi // block, bj // block] = float(
                np.abs(f2[bi:bi + block, bj:bj + block] - ref).mean())
            best_sad, best_dy, best_dx = 1e18, 0, 0
            for dy in range(-search, search + 1):
                for dx in range(-search, search + 1):
                    yi, xi = bi + dy, bj + dx
                    if yi < 0 or xi < 0 or yi + block > H or xi + block > W:
                        continue
                    cand = f2[yi:yi + block, xi:xi + block]
                    sad = float(np.abs(ref - cand).sum())
                    if sad < best_sad:
                        best_sad, best_dy, best_dx = sad, dy, dx
            flow_y[bi // block, bj // block] = best_dy
            flow_x[bi // block, bj // block] = best_dx
    return flow_y, flow_x, sig


def motion_summary(flow_y, flow_x, sig=None, sig_threshold=0.02):
    """运动摘要：主方向 + 平均位移（帧差显著性过滤——防静态/渐变误报）
    真实运动块（帧差显著）才统计；静止块忽略"""
    if sig is not None:
        active = sig > sig_threshold
    else:
        active = np.sqrt(flow_y ** 2 + flow_x ** 2) > 1e-3
    if not active.any():
        return {"moving": False, "direction": "静止", "speed": 0.0,
                "active_blocks": 0}
    ay = float(flow_y[active].mean())
    ax = float(flow_x[active].mean())
    if abs(ax) >= abs(ay):
        direction = "向右" if ax > 0 else "向左"
    else:
        direction = "向下" if ay > 0 else "向上"
    return {"moving": True, "direction": direction,
            "speed": round(float(np.sqrt(ay ** 2 + ax ** 2)), 3),
            "active_blocks": int(active.sum())}


def edges_accuracy(detected_mag, ground_truth, threshold=0.3):
    """边缘检测准确率：检测幅值>阈值的像素 vs 真实边缘像素"""
    pred = (detected_mag > threshold).astype(np.float32)
    gt = np.asarray(ground_truth, dtype=np.float32)
    tp = float((pred * gt).sum())
    fn = float(((1 - pred) * gt).sum())
    fp = float((pred * (1 - gt)).sum())
    precision = tp / (tp + fp + 1e-9)
    recall = tp / (tp + fn + 1e-9)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)
    return {"precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(f1, 3)}


if __name__ == "__main__":
    print("=== 白箱图像处理算法（真实图像→时空原语 · 零 LLM）===\n")

    # ① 合成「真实风格」图像：渐变背景 + 方块
    H = W = 64
    bg = np.zeros((H, W), dtype=np.float32)
    for i in range(H):
        bg[i, :] = i / H  # 垂直渐变（真实图像常见）
    img1 = bg.copy()
    img1[20:36, 10:26] = 0.9  # 方块
    print("① 合成真实风格图像（渐变背景+方块）")

    # ② Sobel 边缘
    mag, ang = sobel(img1)
    edge_mask = mag > 0.3
    # 方块边缘真实位置（上下左右边界）
    gt = np.zeros((H, W), dtype=np.float32)
    gt[20, 10:26] = gt[35, 10:26] = 1
    gt[20:36, 10] = gt[20:36, 25] = 1
    acc = edges_accuracy(mag, gt)
    print(f"② Sobel 边缘: precision={acc['precision']} recall={acc['recall']} "
          f"F1={acc['f1']}")

    # ③ 光流（方块右移 3px）
    img2 = bg.copy()
    img2[20:36, 13:29] = 0.9  # 右移 3
    fy, fx, sig = optical_flow_block(img1, img2, block=8, search=5)
    ms = motion_summary(fy, fx, sig)
    print(f"③ 块匹配光流: 方向={ms['direction']} 位移={ms['speed']}px "
          f"活跃块={ms['active_blocks']}")

    # ④ 静态对照（帧差显著性 → 静止）
    fy0, fx0, sig0 = optical_flow_block(img1, img1, block=8, search=5)
    ms0 = motion_summary(fy0, fx0, sig0)
    print(f"④ 静态对照: 方向={ms0['direction']} 移动={ms0['moving']}")

    print(f"\n=== 判定 ===\n边缘 F1={acc['f1']} | 光流方向={ms['direction']} "
          f"(期望 向右 位移≈3)")
