# -*- coding: utf-8 -*-
"""test_scene_detect_bridge.py · 目标检测↔3D 场景融合测试（第五阶段·lingshu_see 接入）
验证：①场景图→PNG 渲染 ②检测↔3D 对照（投影最近匹配）③融合一致性 ④缺失检测诚实标注"""
import sys, os, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from vision_3d import (synth_stereo_pair, stereo_disparity,
                       depth_from_disparity, pointcloud_from_depth)
from scene_graph import build_scene_graph
from world3d_render import World3DCamera
from scene_detect_bridge import (scene_to_png, detect_to_scene, fusion_consistency)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

left, right = synth_stereo_pair()
pts = pointcloud_from_depth(depth_from_disparity(stereo_disparity(left, right)))
scene = build_scene_graph(pts)

# ① 场景图 → PNG
tmp = tempfile.mkdtemp(prefix="sdb_")
png = os.path.join(tmp, "scene.png")
scene_to_png(scene, png, W=160, H=160)
check('① 场景图渲染 PNG', os.path.isfile(png) and os.path.getsize(png) > 100,
      f'{os.path.getsize(png) if os.path.isfile(png) else 0} bytes')

# 构造检测：每个物体按其投影中心生成 bbox（模拟 lingshu_see）
cam = World3DCamera()
dets = []
for o in scene["objects"]:
    uv, z, vis = cam.project([o["cx"], o["cy"], o["cz"]], 160, 160)
    s = o["size"] / 2.0
    dets.append({"label": "方块" if o["category"] == "近景物体" else "背景",
                 "bbox": [int(uv[0][0] - s * 8), int(uv[0][1] - s * 8),
                          int(uv[0][0] + s * 8), int(uv[0][1] + s * 8)]})

# ② 检测↔3D 对照
fused = detect_to_scene(dets, scene)
check('②a 全部物体被匹配', fused["matched"] == len(scene["objects"]),
      f'matched={fused["matched"]}/{len(scene["objects"])}')
check('②b 融合带语义标注', all(o.get("det_label") for o in fused["objects"]),
      str([(o["category"], o.get("det_label")) for o in fused["objects"]]))

# ③ 融合一致性
c = fusion_consistency(fused)
check('③ 命中率100%+对齐误差有值', c["hit_rate"] == 1.0 and c["avg_align_err"] is not None,
      f'hit={c["hit_rate"]} err={c["avg_align_err"]}')

# ④ 缺失检测诚实标注（只给一个检测 → 另一个 det_label=None）
fused2 = detect_to_scene(dets[:1], scene)
undet = [o for o in fused2["objects"] if o.get("det_label") is None]
check('④ 缺失检测诚实标注', len(undet) >= 1 and fused2["unmatched"] == [],
      f'未检测物体数={len(undet)}')

# ⑤ 对齐误差阈值：错误位置检测不被匹配
bad_det = [{"label": "噪音", "bbox": [0, 0, 5, 5]}]
fused3 = detect_to_scene(bad_det, scene, max_gap=5.0)
check('⑤ 远位置检测不误配', fused3["matched"] == 0 and len(fused3["unmatched"]) == 1,
      f'matched={fused3["matched"]}')

shutil.rmtree(tmp, ignore_errors=True)

print(f'\n=== 检测↔3D 融合测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
