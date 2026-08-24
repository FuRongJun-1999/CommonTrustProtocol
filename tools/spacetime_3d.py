# -*- coding: utf-8 -*-
"""spacetime_3d.py · 3D 时空轨迹（第五阶段·时间×空间闭环）
多帧双目 → 逐帧 3D 场景图 → 跨帧追踪 → 3D 运动轨迹（方向/速度/位移）
衔接：stcnn 2D 帧运动原语 ↔ 本模块 3D 空间运动——2D 是 3D 透视下的情况。
零 LLM 确定性。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
try:
    from vision_3d import (synth_stereo_pair, stereo_disparity,
                           depth_from_disparity, pointcloud_from_depth)
    from scene_graph import build_scene_graph
except ImportError:
    from .vision_3d import (synth_stereo_pair, stereo_disparity,
                            depth_from_disparity, pointcloud_from_depth)
    from .scene_graph import build_scene_graph


def synth_moving_stereo_frames(frames=10, speed_px=2, direction="right",
                               size=64, fg_rows=(20, 36), fg_left=(10, 26)):
    """合成移动双目序列：前景球逐帧平移（speed_px/帧，direction: right/left/up）
    返回 [(left, right), ...]（每帧独立双目对）"""
    seq = []
    for t in range(frames):
        shift = speed_px * t
        if direction == "left":
            left_col = max(24 - shift, 10)  # 左移从 x=24 起（对称右移），钳制避免贴边界
        elif direction == "up":
            left_col = fg_left[0]
            fg_rows_t = (fg_rows[0] - shift, fg_rows[1] - shift)
            left, right = synth_stereo_pair(size=size, fg_rows=fg_rows_t,
                                            fg_left=left_col)
            seq.append((left, right))
            continue
        else:
            left_col = fg_left[0] + shift
        left, right = synth_stereo_pair(size=size, fg_rows=fg_rows,
                                        fg_left=(left_col, left_col + 16))
        seq.append((left, right))
    return seq


def frame_scene_graphs(seq, block=8):
    """每帧 双目→点云→场景图 → 近景物体 3D 质心序列
    返回 [{"t", "near": {"cx","cy","cz"} | None, "scene": 场景图}]"""
    out = []
    for t, (left, right) in enumerate(seq):
        disp = stereo_disparity(left, right, block=block, search=16)
        depth = depth_from_disparity(disp)
        pts = pointcloud_from_depth(depth, block=block)
        sg = build_scene_graph(pts)
        near = next((o for o in sg["objects"] if o["category"] == "近景物体"), None)
        out.append({"t": t, "near": near, "scene": sg})
    return out


def track_3d(frame_graphs, max_gap=30.0):
    """跨帧 3D 追踪：近景物体逐帧最近邻匹配（3D 距离最小且 < max_gap）
    返回 轨迹: [{"t", "x", "y", "z"}, ...]（丢帧处断开，返回最长连续段）"""
    positions = []
    for f in frame_graphs:
        n = f.get("near")
        positions.append(None if n is None else (n["cx"], n["cy"], n["cz"]))
    # 逐帧贪心最近邻（前一帧物体 → 本帧最近）
    trajectory = []
    prev = None
    for t, pos in enumerate(positions):
        if pos is None:
            continue
        if prev is not None:
            d = float(np.hypot(pos[0] - prev[0], pos[2] - prev[2]))
            if d > max_gap:  # 跳变 → 新轨迹起点
                trajectory = []
        trajectory.append({"t": t, "x": pos[0], "y": pos[1], "z": pos[2]})
        prev = pos
    return trajectory


def motion_3d(trajectory):
    """轨迹 → 3D 运动原语：主轴方向(±x/±z)、速度(单位/帧)、位移向量、一致性
    一致性 = 主轴方向不变帧占比（直线运动 → 1.0）"""
    if len(trajectory) < 2:
        return {"ok": False, "reason": "轨迹过短（<2 帧）", "direction": "静止",
                "speed": 0.0, "displacement": [0, 0, 0], "consistency": 0.0}
    xs = [p["x"] for p in trajectory]
    zs = [p["z"] for p in trajectory]
    dx, dz = xs[-1] - xs[0], zs[-1] - zs[0]
    frames = len(trajectory) - 1

    def monotonic(vals):
        """单调性分数：递增/递减帧占比最大值（直线运动 → 1.0）"""
        inc = sum(1 for i in range(1, len(vals)) if vals[i] > vals[i - 1])
        dec = sum(1 for i in range(1, len(vals)) if vals[i] < vals[i - 1])
        return max(inc, dec) / max(1, len(vals) - 1)

    # 主轴判定：单调性最高的轴（抗视差匹配噪声——真实位移单调，噪声波动非单调）
    main_axis = "x" if monotonic(xs) >= monotonic(zs) else "z"
    if main_axis == "x":
        direction = ["x+" if dx > 0 else "x-"] if abs(dx) > 1e-3 else ["静止"]
    else:
        direction = ["z+" if dz > 0 else "z-"] if abs(dz) > 1e-3 else ["静止"]
    speed = abs(dx if main_axis == "x" else dz) / max(frames, 1)
    # 一致性：主轴方向一致占比（零位移帧=量化停顿，跳过不参与）
    agrees, compared = 0, 0
    for i in range(1, len(trajectory) - 1):
        d1 = (trajectory[i]["x"] - trajectory[i - 1]["x"],
              trajectory[i]["z"] - trajectory[i - 1]["z"])
        d2 = (trajectory[i + 1]["x"] - trajectory[i]["x"],
              trajectory[i + 1]["z"] - trajectory[i]["z"])
        v = d1[0] if main_axis == "x" else d1[1]
        w = d2[0] if main_axis == "x" else d2[1]
        if v == 0 or w == 0:
            continue  # 量化停顿帧不参与方向判定
        compared += 1
        if v * w > 0:
            agrees += 1
    consistency = agrees / max(1, compared)
    return {"ok": True, "direction": direction,
            "speed": round(speed, 3), "displacement": [round(dx, 2), 0.0, round(dz, 2)],
            "consistency": round(consistency, 3), "frames": len(trajectory)}


if __name__ == "__main__":
    print("=== 3D 时空轨迹：时间×空间闭环（零 LLM）===\n")
    seq = synth_moving_stereo_frames(frames=10, speed_px=2, direction="right")
    fgs = frame_scene_graphs(seq)
    traj = track_3d(fgs)
    print(f"① 合成双目序列: {len(seq)} 帧（球逐帧右移 speed=2px/帧）")
    print(f"② 逐帧场景图: 近景物体 3D 质心 = "
          f"{[(f['t'], f['near']['cx'] if f['near'] else None) for f in fgs]}")
    print(f"③ 3D 轨迹: {[(p['t'], round(p['x'], 1)) for p in traj]}")
    m = motion_3d(traj)
    print(f"④ 3D 运动原语: 方向={m.get('direction')} 速度={m.get('speed')} 单位/帧 "
          f"位移={m.get('displacement')} 一致性={m.get('consistency')}")
    ok = m.get("ok") and m.get("direction") == ["x+"] and 1.5 < m.get("speed") < 3.0
    print(f"\n=== 判定 ===\n3D 时空轨迹: "
          f"{'✔ 方向/速度/轨迹成立（2D 运动升级 3D 空间运动）' if ok else '✘'}")
