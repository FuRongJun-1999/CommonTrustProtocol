# -*- coding: utf-8 -*-
"""world3d_render.py · 3D 时空视觉闭环 ③语义→3D 渲染（WORLD3D 同款相机模型）
场景图 → 3D 世界（物体=彩色立方体 bbox）→ 透视投影渲染（fov/yaw/pitch，同灵枢 WORLD3D）
输出渲染深度图 + 类别图 + 物体投影（bbox 中心/面积/深度）——供闭环自校验对照。
零 LLM 确定性——「描述的 3D 世界」的确定性投影（2D 是 3D 透视下的情况）。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
try:
    from scene_graph import CATEGORY_COLOR
except ImportError:
    from .scene_graph import CATEGORY_COLOR


class World3DCamera:
    """与灵枢 WORLD3D 同款相机模型：fov_deg=60, 位置(cx,cy,cz), yaw/pitch 视角"""

    def __init__(self, fov_deg=60.0, cx=0.0, cy=1.2, cz=0.0, yaw=0.0, pitch=0.0):
        self.fov = np.radians(fov_deg)
        self.cx, self.cy, self.cz = cx, cy, cz
        self.yaw, self.pitch = yaw, pitch

    def project(self, world_pts, W=128, H=128):
        """世界点 (N,3) → 相机坐标 → 透视投影 → 像素 (u,v) + 相机深度 z_cam
        返回 (uv, z_cam, visible)：visible = 相机前方(z_cam>0) 且在视锥内"""
        pts = np.asarray(world_pts, dtype=np.float64)
        if pts.ndim == 1:
            pts = pts[None, :]
        # 平移：世界 → 相机坐标原点
        pc = pts - np.array([self.cx, self.cy, self.cz])
        # yaw 绕 Y 轴、pitch 绕 X 轴（负号：相机朝 -Z）
        cy, sy = np.cos(self.yaw), np.sin(self.yaw)
        cp, sp = np.cos(self.pitch), np.sin(self.pitch)
        R = np.array([[cy, 0.0, sy],
                      [sy * sp, cp, -cy * sp],
                      [-sy * cp, sp, cy * cp]])
        cam = pc @ R.T
        z = cam[:, 2]
        fx = (W / 2.0) / np.tan(self.fov / 2.0)
        fy = fx
        visible = z > 0.1
        u = W / 2.0 + fx * cam[:, 0] / np.maximum(z, 1e-6)
        v = H / 2.0 - fy * cam[:, 1] / np.maximum(z, 1e-6)
        visible &= (u >= 0) & (u < W) & (v >= 0) & (v < H)
        return np.stack([u, v], axis=1), z, visible


def render_scene(scene, W=128, H=128, camera=None):
    """场景图 → 3D 世界 → 透视渲染
    每个物体 = 以 (cx, cy=cz 作为深度轴? 否——cz 即 z 深度) 为中心的彩色立方体
    约定：场景图物体 (cx, cy, cz) → 3D 世界坐标 (x=cx, y=cy, z=cz)
    输出: {"depth": 深度图, "labels": 类别图, "objects": [投影几何], "camera": params}"""
    camera = camera or World3DCamera()
    objects = scene.get("objects", [])
    depth_img = np.full((H, W), 1e9, dtype=np.float32)
    label_img = np.zeros((H, W), dtype=np.int32)
    projections = []
    for o in objects:
        s = o["size"] / 2.0
        # 立方体 8 顶点（世界坐标）
        corners = np.array([[o["cx"] - s, o["cy"] - s, o["cz"] - s],
                            [o["cx"] + s, o["cy"] - s, o["cz"] - s],
                            [o["cx"] - s, o["cy"] + s, o["cz"] - s],
                            [o["cx"] + s, o["cy"] + s, o["cz"] - s],
                            [o["cx"] - s, o["cy"] - s, o["cz"] + s],
                            [o["cx"] + s, o["cy"] - s, o["cz"] + s],
                            [o["cx"] - s, o["cy"] + s, o["cz"] + s],
                            [o["cx"] + s, o["cy"] + s, o["cz"] + s]])
        uv, z, vis = camera.project(corners, W, H)
        if not vis.any():
            continue
        u, v = uv[:, 0], uv[:, 1]
        umin, umax = max(0, int(u.min())), min(W, int(u.max()) + 1)
        vmin, vmax = max(0, int(v.min())), min(H, int(v.max()) + 1)
        zc = float(z[vis].mean())
        # 画立方体正面（z 均值深度）
        for i in range(vmin, vmax):
            for j in range(umin, umax):
                if depth_img[i, j] > zc:
                    depth_img[i, j] = zc
                    label_img[i, j] = o["id"] + 1
        projections.append({"id": o["id"], "category": o["category"],
                            "u": round(float(np.clip(uv[0][0], 0, W)), 2),
                            "v": round(float(np.clip(uv[1][0], 0, H)), 2),
                            "z": round(zc, 2),
                            "bbox": [umin, vmin, umax, vmax],
                            "area": max(1, (umax - umin) * (vmax - vmin)),
                            "world_cz": o["cz"]})
    return {"depth": depth_img, "labels": label_img,
            "objects": projections,
            "camera": {"fov_deg": np.degrees(camera.fov), "cx": camera.cx,
                       "cy": camera.cy, "cz": camera.cz,
                       "yaw": camera.yaw, "pitch": camera.pitch}}


if __name__ == "__main__":
    print("=== 3D 时空视觉闭环 ③：场景图 → 3D 渲染（WORLD3D 同款相机）===\n")
    from scene_graph import build_scene_graph
    from vision_3d import (synth_stereo_pair, stereo_disparity,
                           depth_from_disparity, pointcloud_from_depth)

    left, right = synth_stereo_pair()
    pts = pointcloud_from_depth(depth_from_disparity(stereo_disparity(left, right)))
    sg = build_scene_graph(pts)
    print("① 场景图:", [(o["category"], o["cz"]) for o in sg["objects"]])

    cam = World3DCamera(yaw=0.0, pitch=0.0)
    render = render_scene(sg, W=128, H=128, camera=cam)
    print("② 渲染深度图: 有效像素 =", int((render["depth"] < 1e8).sum()))
    for p in render["objects"]:
        print(f"   [{p['id']}] {p['category']} 投影中心=({p['u']:.0f},{p['v']:.0f}) "
              f"z={p['z']} bbox面积={p['area']} 世界深度={p['world_cz']}")

    # 近大远小判定：近景物体（世界 z 小）投影面积应更大/深度更小
    objs = render["objects"]
    near = [o for o in objs if o["category"] == "近景物体"]
    far = [o for o in objs if o["category"] == "远景物体"]
    ok = (near and far and near[0]["area"] > far[0]["area"]
          and near[0]["z"] < far[0]["z"])
    print(f"\n=== 判定 ===\n语义→3D 渲染: "
          f"{'✔ 近大远小/近深小成立（2D 是 3D 透视下的情况）' if ok else '✘'}")
