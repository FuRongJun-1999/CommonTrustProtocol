# -*- coding: utf-8 -*-
"""spacetime_projection.py · 2D↔3D 投影互校验（第五阶段·闭环时间维自校验）
同一运动的两个视图互相印证（2D 是 3D 透视下的情况）：
  2D 侧：左目帧序列 → stcnn 2D 运动原语（方向/速度 px/帧）
  3D 侧：双目序列 → spacetime_3d 3D 轨迹（主轴方向/速度 单位/帧）
互校验：方向映射（向右↔x+，向左↔x-，静止↔静止）+ 速度互验（3D×10 ≈ 2D）
→ 一致性 = 白箱对自身感知的置信度（防单视图幻觉）。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    from stcnn import extract_spatiotemporal_primitives
    from spacetime_3d import frame_scene_graphs, track_3d, motion_3d
except ImportError:
    from .stcnn import extract_spatiotemporal_primitives
    from .spacetime_3d import frame_scene_graphs, track_3d, motion_3d


# 2D 方向 ↔ 3D 主轴方向映射（图像列增 = 世界 x 增）
DIRECTION_MAP = {
    ("向右", "x+"): True, ("向右", "x-"): False,
    ("向左", "x-"): True, ("向左", "x+"): False,
    ("静止", "静止"): True, ("向右", "z+"): False, ("向右", "z-"): False,
    ("向左", "z+"): False, ("向左", "z-"): False,
    # 冲突组合（单视图矛盾：一侧运动另一侧静止）
    ("向右", "静止"): False, ("向左", "静止"): False,
    ("静止", "x+"): False, ("静止", "x-"): False,
    ("静止", "z+"): False, ("静止", "z-"): False,
}

# 3D x 尺度 = 像素/10（pointcloud_from_depth: x=(j*8+4)/10）
PIXEL_SCALE = 10.0


def direction_map(d2, d3):
    """2D 方向与 3D 主轴方向一致性（True=一致）"""
    return DIRECTION_MAP.get((d2, d3), False)


def cross_validate(stereo_seq, speed_tol=0.30):
    """双目序列 → 2D/3D 双侧运动原语 → 互校验
    返回 {ok, d2, d3, speed2, speed3, speed_err, checks}"""
    # 2D 侧：左目帧序列 → stcnn 时空原语
    left_frames = [left for left, _ in stereo_seq]
    prims2, _ = extract_spatiotemporal_primitives(left_frames)
    d2 = prims2["direction"]
    speed2 = float(prims2["speed"])

    # 3D 侧：双目序列 → 3D 轨迹 → 3D 运动原语
    traj = track_3d(frame_scene_graphs(stereo_seq))
    m3 = motion_3d(traj)
    d3 = m3.get("direction", ["静止"])[0] if m3.get("ok") else "静止"
    speed3 = float(m3.get("speed", 0.0))

    # 方向一致性
    dir_ok = direction_map(d2, d3)
    # 速度互验：3D speed × 尺度 vs 2D speed（相对误差）
    speed3_px = speed3 * PIXEL_SCALE
    denom = max(speed2, 1e-6)
    speed_err = abs(speed3_px - speed2) / denom if speed2 > 0 else abs(speed3_px)
    speed_ok = speed_err <= speed_tol or (speed2 == 0 and speed3 == 0)

    checks = {"方向映射": f"{d2}↔{d3} {'✔' if dir_ok else '✘'}",
              "速度互验": f"3D {speed3:.3f}×10={speed3_px:.2f} vs 2D {speed2:.2f}px/帧 "
                          f"(误差 {speed_err:.2%}) {'✔' if speed_ok else '✘'}"}
    ok = dir_ok and speed_ok
    return {"ok": ok, "d2": d2, "d3": d3, "speed2": round(speed2, 3),
            "speed3": round(speed3, 3), "speed_err": round(speed_err, 3),
            "checks": checks}


if __name__ == "__main__":
    print("=== 2D↔3D 投影互校验：同一运动两视图互证（零 LLM）===\n")
    from spacetime_3d import synth_moving_stereo_frames
    for label, seq in [
        ("右移球", synth_moving_stereo_frames(frames=10, speed_px=2, direction="right")),
        ("左移球", synth_moving_stereo_frames(frames=8, speed_px=2, direction="left")),
        ("静止背景", synth_moving_stereo_frames(frames=6, speed_px=0, direction="right")),
    ]:
        r = cross_validate(seq)
        mark = "✔" if r["ok"] else "✘"
        print(f"[{mark}] {label}: 2D={r['d2']}({r['speed2']}px/帧) "
              f"3D={r['d3']}({r['speed3']}单位/帧)")
        for k, v in r["checks"].items():
            print(f"   {k}: {v}")
    ok_all = all(cross_validate(seq)["ok"] for seq in [
        synth_moving_stereo_frames(frames=10, speed_px=2, direction="right"),
        synth_moving_stereo_frames(frames=8, speed_px=2, direction="left"),
        synth_moving_stereo_frames(frames=6, speed_px=0, direction="right")])
    print(f"\n=== 判定 ===\n2D↔3D 投影互校验: "
          f"{'✔ 两视图互证成立（感知自校验时间维）' if ok_all else '✘'}")
