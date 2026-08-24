# -*- coding: utf-8 -*-
"""test_spatial_closure.py · 3D 时空视觉闭环测试（第五阶段·感知↔语义双向）
验证：①感知→场景图（近/远景聚类）②语义→3D 渲染（近大远小）③闭环一致性≥0.8
④时空原语附注 ⑤不同视角渲染稳定"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from vision_3d import (synth_stereo_pair, stereo_disparity,
                       depth_from_disparity, pointcloud_from_depth)
from scene_graph import build_scene_graph, cluster_pointcloud
from world3d_render import World3DCamera, render_scene
from spatial_closure import spatial_closure

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

left, right = synth_stereo_pair()
pts = pointcloud_from_depth(depth_from_disparity(stereo_disparity(left, right)), block=8)

# ① 感知 → 场景图：近/远景两类，近景在前
sg = build_scene_graph(pts, motion={"direction": "静止", "speed": 0, "is_static": True})
cats = [o["category"] for o in sg["objects"]]
check('①a 场景图两类物体', sg["count"] >= 2 and "近景物体" in cats and "远景物体" in cats,
      f'{sg["count"]} 物体: {cats}')
check('①b 近景在前', sg["objects"][0]["category"] == "近景物体"
      and sg["objects"][0]["cz"] < sg["objects"][-1]["cz"],
      f'近景 z={sg["objects"][0]["cz"]} < 远景 z={sg["objects"][-1]["cz"]}')
check('①c 时空原语附注', sg["objects"][0].get("motion", {}).get("direction") == "静止",
      str(sg["objects"][0].get("motion")))

# ② 语义 → 3D 渲染：近大远小（近景投影面积大、深度小）
cam = World3DCamera()
render = render_scene(sg, W=128, H=128, camera=cam)
near = [o for o in render["objects"] if o["category"] == "近景物体"]
far = [o for o in render["objects"] if o["category"] == "远景物体"]
if near and far:
    check('②a 近大远小', near[0]["area"] > far[0]["area"],
          f'近 area={near[0]["area"]} > 远 area={far[0]["area"]}')
    check('②b 近深小', near[0]["z"] < far[0]["z"], f'近 z={near[0]["z"]} < 远 z={far[0]["z"]}')
else:
    check('②a 近大远小', False, '渲染缺近/远物体')
    check('②b 近深小', False, '渲染缺近/远物体')

# ③ 闭环一致性 ≥0.8
r = spatial_closure(pts, motion={"direction": "静止", "speed": 0, "is_static": True})
check('③ 闭环一致性≥0.8', r.get("ok") and r.get("consistency", 0) >= 0.8,
      f'consistency={r.get("consistency")} checks={r.get("checks")}')

# ④ 不同视角渲染稳定（yaw 偏转后仍有近/远物体投影）
cam2 = World3DCamera(yaw=0.3, pitch=0.1)
render2 = render_scene(sg, W=128, H=128, camera=cam2)
check('④ 视角偏转渲染稳定', len(render2["objects"]) >= 2,
      f'{len(render2["objects"])} 物体 @ yaw=0.3')

# ⑤ 空点云诚实边界
r0 = spatial_closure([], camera=cam)
check('⑤ 空点云诚实边界', not r0.get("ok") and "不足" in r0.get("reason", ""),
      r0.get("reason"))

print(f'\n=== 3D 时空视觉闭环测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
