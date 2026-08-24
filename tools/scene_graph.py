# -*- coding: utf-8 -*-
"""scene_graph.py · 3D 时空视觉闭环 ①感知→语义：点云+时空原语 → 场景图
白箱自身视觉的语义出口：3D 点云（感知）→ 空间锚点聚类 → 场景图
  {物体: [类别, 质心(x,y), 尺寸, 深度z, 运动原语, 颜色]}
零 LLM 确定性——「看见了什么」的结构化表达（衔接 WORLD3D 语义→3D 的反向输入）。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')


def cluster_pointcloud(pts, depth_gap=20.0):
    """点云按深度聚类：近景组/远景组（白箱无监督：深度差分组）
    pts: [(x, y, z), ...]（vision_3d pointcloud 输出）
    返回: [{"cx","cy","cz","size","count","category"}, ...]"""
    if not pts:
        return []
    arr = np.asarray(pts, dtype=np.float32)
    order = np.argsort(arr[:, 2])  # 按深度升序（近→远）
    sorted_pts = arr[order]
    groups = []
    cur = [sorted_pts[0]]
    for p in sorted_pts[1:]:
        if p[2] - cur[-1][2] > depth_gap:  # 深度跳变 → 新组
            groups.append(cur)
            cur = [p]
        else:
            cur.append(p)
    groups.append(cur)
    objects = []
    for g in groups:
        g = np.asarray(g)
        cx, cy, cz = g[:, 0].mean(), g[:, 1].mean(), g[:, 2].mean()
        size = max(float(g[:, 0].max() - g[:, 0].min()),
                   float(g[:, 1].max() - g[:, 1].min()),
                   float(g[:, 2].max() - g[:, 2].min())) or 1.0
        category = "近景物体" if cz < np.median(arr[:, 2]) else "远景物体"
        objects.append({"id": len(objects), "category": category,
                        "cx": round(float(cx), 2), "cy": round(float(cy), 2),
                        "cz": round(float(cz), 2), "size": round(size, 2),
                        "count": len(g)})
    objects.sort(key=lambda o: o["cz"])  # 近→远
    return objects


# 物体类别 → 3D 颜色（语义→3D 渲染用，同灵枢 WORLD3D 语义色表风格）
CATEGORY_COLOR = {
    "近景物体": (0.90, 0.30, 0.20),   # 红橙（近）
    "远景物体": (0.25, 0.45, 0.85),   # 蓝（远）
    "背景":     (0.55, 0.55, 0.55),
}


def attach_motion(scene_objects, motion=None):
    """时空原语附注：stcnn 运动原语（方向/速度/周期/静止）挂到最近物体
    motion: stcnn extract_spatiotemporal_primitives 输出或 {"direction": "向右", ...}"""
    if not motion or not scene_objects:
        return scene_objects
    for o in scene_objects:
        o["motion"] = {"direction": motion.get("direction", "静止"),
                       "speed": motion.get("speed", 0),
                       "period": motion.get("period"),
                       "is_static": motion.get("is_static", True)}
    return scene_objects


def build_scene_graph(pts, motion=None):
    """感知 → 场景图（闭环 ①）：点云聚类 + 时空原语附注"""
    objects = cluster_pointcloud(pts)
    objects = attach_motion(objects, motion)
    return {"objects": objects, "count": len(objects)}


if __name__ == "__main__":
    print("=== 3D 时空视觉闭环 ①：点云 → 场景图（零 LLM）===\n")
    from vision_3d import synth_stereo_pair, stereo_disparity, depth_from_disparity, pointcloud_from_depth

    left, right = synth_stereo_pair()
    disp = stereo_disparity(left, right, block=8, search=16)
    depth = depth_from_disparity(disp)
    pts = pointcloud_from_depth(depth, block=8)
    print(f"① 感知点云: {len(pts)} 点（近景方块 + 远景背景）")

    motion = {"direction": "静止", "speed": 0, "is_static": True}
    sg = build_scene_graph(pts, motion)
    print("\n② 场景图（聚类结果）：")
    for o in sg["objects"]:
        print(f"   [{o['id']}] {o['category']} 质心=({o['cx']},{o['cy']},{o['cz']}) "
              f"尺寸={o['size']} 点数={o['count']} 运动={o.get('motion', {}).get('direction')}")

    ok = sg["count"] >= 2 and sg["objects"][0]["category"] == "近景物体"
    print(f"\n=== 判定 ===\n感知→语义场景图: {'✔ 近/远景聚类成立' if ok else '✘'}")
