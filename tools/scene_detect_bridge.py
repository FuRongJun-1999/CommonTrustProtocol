# -*- coding: utf-8 -*-
"""scene_detect_bridge.py · 目标检测 ↔ 3D 场景融合（第五阶段·lingshu_see 接入）
场景图（3D 几何）→ 投影渲染 PNG → 目标检测（lingshu_see YOLO-World）→
检测 bbox（语义类别）↔ 场景图物体（3D 结构）对照 → 带语义的 3D 场景。
一致性 = 检测命中率 + 位置对齐误差（融合质量度量，零 LLM）。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
try:
    from world3d_render import World3DCamera
except ImportError:
    from .world3d_render import World3DCamera


def scene_to_png(scene, path, W=160, H=160, camera=None, colors=None):
    """场景图 → PIL 渲染 PNG（物体=彩色方块，按 WORLD3D 相机投影画）
    colors: {category: RGB} 覆盖 CATEGORY_COLOR（检测友好色）"""
    from PIL import Image
    camera = camera or World3DCamera()
    colors = colors or {"近景物体": (230, 80, 50), "远景物体": (60, 120, 220)}
    img = np.zeros((H, W, 3), dtype=np.uint8)
    img[:] = (240, 240, 235)  # 浅背景
    for o in scene.get("objects", []):
        s = o["size"] / 2.0
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
        umin, umax = max(0, int(uv[:, 0].min())), min(W, int(uv[:, 0].max()) + 1)
        vmin, vmax = max(0, int(uv[:, 1].min())), min(H, int(uv[:, 1].max()) + 1)
        color = colors.get(o["category"], (120, 120, 120))
        img[vmin:vmax, umin:umax] = color
    Image.fromarray(img).save(path)
    return path


def detect_to_scene(detections, scene, camera=None, W=160, H=160, max_gap=20.0):
    """检测 bbox + 场景图 → 带语义的 3D 场景（投影中心最近匹配）
    detections: [{label, bbox: [x1,y1,x2,y2]}]（lingshu_see 输出）
    返回 {objects: [3D 物体+det 标注], matched, unmatched}"""
    camera = camera or World3DCamera()
    objs = scene.get("objects", [])
    # 物体 3D 质心 → 投影中心
    proj = {}
    for o in objs:
        uv, z, vis = camera.project([o["cx"], o["cy"], o["cz"]], W, H)
        proj[o["id"]] = (float(uv[0][0]), float(uv[0][1]))
    fused, matched, unmatched = [], 0, []
    used = set()
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        dc = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        best_id, best_d = None, 1e18
        for oid, pc in proj.items():
            if oid in used:
                continue
            dist = float(np.hypot(pc[0] - dc[0], pc[1] - dc[1]))
            if dist < best_d:
                best_id, best_d = oid, dist
        if best_id is not None and best_d <= max_gap:
            o = objs[best_id]
            fused.append({**o, "det_label": d["label"], "det_bbox": d["bbox"],
                          "align_err": round(best_d, 2)})
            used.add(best_id)
            matched += 1
        else:
            unmatched.append(d)
    # 未匹配的 3D 物体（无检测）标注 det_label=None
    for o in objs:
        if o["id"] not in used:
            fused.append({**o, "det_label": None, "det_bbox": None, "align_err": None})
    fused.sort(key=lambda x: x["cz"])
    return {"objects": fused, "matched": matched, "unmatched": unmatched,
            "total": len(objs)}


def fusion_consistency(fused):
    """融合一致性：检测命中率 + 位置对齐平均误差"""
    total = len(fused.get("objects", []))
    det = [o for o in fused.get("objects", []) if o.get("det_label")]
    hit_rate = len(det) / max(1, total)
    errs = [o["align_err"] for o in det if o.get("align_err") is not None]
    avg_err = float(np.mean(errs)) if errs else None
    return {"hit_rate": round(hit_rate, 3), "avg_align_err": round(avg_err, 2)
            if avg_err is not None else None, "detected": len(det), "total": total}


if __name__ == "__main__":
    print("=== 目标检测 ↔ 3D 场景融合（零 LLM）===\n")
    import os, tempfile
    from scene_graph import build_scene_graph
    from vision_3d import (synth_stereo_pair, stereo_disparity,
                           depth_from_disparity, pointcloud_from_depth)
    from world3d_render import World3DCamera

    left, right = synth_stereo_pair()
    pts = pointcloud_from_depth(depth_from_disparity(stereo_disparity(left, right)))
    scene = build_scene_graph(pts)
    tmp = tempfile.mkdtemp(prefix="det_")
    png = os.path.join(tmp, "scene.png")
    scene_to_png(scene, png, W=160, H=160)
    print(f"① 场景图 → PNG: {png}（{scene['count']} 物体）")

    # 模拟检测（真实 lingshu_see 冒烟在测试/演示中接入）
    dets = []
    for o in scene["objects"]:
        cam = World3DCamera()
        uv, z, vis = cam.project([o["cx"], o["cy"], o["cz"]], 160, 160)
        s = o["size"] / 2.0
        dets.append({"label": "方块" if o["category"] == "近景物体" else "背景",
                     "bbox": [int(uv[0][0] - s * 8), int(uv[0][1] - s * 8),
                              int(uv[0][0] + s * 8), int(uv[0][1] + s * 8)]})
    fused = detect_to_scene(dets, scene)
    print("② 检测 bbox → 3D 场景对照：")
    for o in fused["objects"]:
        print(f"   [{o['id']}] {o['category']} 检测={o['det_label']} "
              f"对齐误差={o['align_err']}")
    c = fusion_consistency(fused)
    print(f"③ 融合一致性: 命中率={c['hit_rate']} 平均对齐误差={c['avg_align_err']}")
    ok = c["hit_rate"] == 1.0 and c["avg_align_err"] is not None
    print(f"\n=== 判定 ===\n检测↔3D 融合: "
          f"{'✔ 语义+几何融合成立（命中率100%）' if ok else '✘'}")
