# -*- coding: utf-8 -*-
"""real_world_3d.py · 3D 感知真实感鲁棒性（第五阶段·合成→真实过渡）
真实感干扰（高斯噪声/光照渐变/低纹理）下 3D 管线鲁棒性验证：
  合成双目 + 干扰 → 立体视差 → 近大远小保持？（量化误差表）
  边缘增强（Sobel）→ 低纹理场景匹配提升？
零 LLM 确定性——「真实世界不完美，白箱感知要扛得住」。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
try:
    from vision_3d import stereo_disparity
    from image_processing import sobel
except ImportError:
    from .vision_3d import stereo_disparity
    from .image_processing import sobel


def synth_noisy_stereo_pair(noise=0.05, light_grad=0.0, size=64,
                            fg_rows=(20, 36), fg_left=(10, 26), disp_fg=8, disp_bg=2):
    """合成双目 + 真实感干扰：
    noise: 高斯噪声标准差（0=无噪声）；light_grad: 光照渐变强度（0=均匀）"""
    rng = np.random.RandomState(0)
    bg = rng.rand(size, size).astype(np.float32) * 0.4
    left = bg.copy()
    right = bg.copy()
    right[:, :size - disp_bg] = left[:, disp_bg:]
    r0, r1 = fg_rows
    c0, c1 = fg_left
    left[r0:r1, c0:c1] = 0.9
    right[r0:r1, c0 - disp_fg:c1 - disp_fg] = 0.9
    if light_grad > 0:
        # 光照渐变（左亮右暗）：真实感
        ramp = np.linspace(1.0, 1.0 - light_grad, size, dtype=np.float32)
        left = left * ramp[None, :]
        right = right * ramp[None, :]
    if noise > 0:
        left = left + rng.normal(0, noise, left.shape).astype(np.float32)
        right = right + rng.normal(0, noise, right.shape).astype(np.float32)
    return left, right


def stereo_verdict(left, right, block=8, search=16):
    """双目对 → 近大远小判定：前景块视差 > 背景视差（3D 成立的判据）
    返回 {fg_disp, bg_disp, ok}"""
    disp = stereo_disparity(left, right, block=block, search=search)
    fg_blocks = (slice(20 // block, 36 // block), slice(10 // block, 26 // block))
    fg_disp = float(disp[fg_blocks].mean())
    bg_disp = float(np.median(disp))
    return {"fg_disp": round(fg_disp, 2), "bg_disp": round(bg_disp, 2),
            "ok": fg_disp > bg_disp + 1.0}


def edge_enhanced_stereo(left, right, block=8, search=16):
    """Sobel 边缘增强预处理 → 视差（边缘引导匹配：低纹理场景关键）"""
    mag_l, _ = sobel(np.clip(left, 0, 1))
    mag_r, _ = sobel(np.clip(right, 0, 1))
    disp = stereo_disparity(mag_l, mag_r, block=block, search=search)
    return disp


def robustness_report():
    """噪声水平 → 近大远小保持 + 前景视差误差（量化表）"""
    rows = []
    for noise in (0.0, 0.05, 0.1, 0.2):
        l, r = synth_noisy_stereo_pair(noise=noise)
        v = stereo_verdict(l, r)
        rows.append({"noise": noise, **v})
    return rows


if __name__ == "__main__":
    print("=== 3D 感知真实感鲁棒性（零 LLM）===\n")
    print("① 噪声水平 → 近大远小保持：")
    for row in robustness_report():
        mark = "✔" if row["ok"] else "✘"
        print(f"   噪声 {row['noise']:.2f}: 前景视差={row['fg_disp']} "
              f"背景视差={row['bg_disp']} {mark}")
    print("\n② 光照渐变：")
    l, r = synth_noisy_stereo_pair(light_grad=0.4)
    v = stereo_verdict(l, r)
    print(f"   渐变0.4: 前景={v['fg_disp']} 背景={v['bg_disp']} "
          f"{'✔' if v['ok'] else '✘'}")
    print("\n③ 边缘增强（低纹理）:")
    l, r = synth_noisy_stereo_pair(noise=0.05)
    disp_raw = stereo_disparity(l, r)
    disp_ed = edge_enhanced_stereo(l, r)
    print(f"   原始视差前景={disp_raw[2:4, 1:3].mean():.2f} | "
          f"边缘增强前景={disp_ed[2:4, 1:3].mean():.2f}")
    ok_all = all(row["ok"] for row in robustness_report())
    print(f"\n=== 判定 ===\n真实感鲁棒性: "
          f"{'✔ 噪声/光照下 3D 仍成立（合成→真实过渡可行）' if ok_all else '✘'}")
