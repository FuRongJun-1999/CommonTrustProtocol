# -*- coding: utf-8 -*-
"""test_attention · 里程碑4.4 注意力驱动的递归细化测试
（提示词条件权重/世界重要性/递归层数/递归盒数/朝向/确定性）"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web import attention as A
from aeis.game_web.generate import WorldGenerator, parse_scene
from aeis.game_web.render3d import entity_boxes, _facing

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 1. 提示词条件权重 ----------
text = "森林里有狼追兔子，湖边有一只守卫"
spec = parse_scene(text, 24)
pw = A.prompt_attention(text, spec)
check("chased rabbit highest", pw.get("rabbit", 0) > pw.get("wolf", 0)
      and pw.get("rabbit", 0) >= 0.8, str(pw))
check("mentioned guard boosted", pw.get("guard", 0) > 0.5, str(pw))
check("all in [0,1]", all(0 <= v <= 1 for v in pw.values()), str(pw))

# 焦点词提升
pw2 = A.prompt_attention("重点关注那只狼", parse_scene("森林里有狼追兔子", 24))
check("focus word boosts", pw2.get("wolf", 0) >= 0.8, str(pw2))

# ---------- 2. 世界模型重要性 + 组合 ----------
gen = WorldGenerator(size=24, seed=42)
loop = gen.build_world(spec)
for _ in range(10):
    loop.step()
ww = A.world_attention(loop, spec)
check("world attention computed", all(c in ww for c in pw), str(ww))
amap = A.attention_map(text, spec, loop)
check("combined attention", all(amap[c] >= pw[c] - 1e-6 for c in pw), str(amap))
depths = {c: A.recursion_depth(w) for c, w in amap.items()}
check("chase pair deeper than guard", depths["rabbit"] >= depths["guard"]
      and depths["wolf"] >= depths["guard"], str(depths))
check("depth in [0,3]", all(0 <= v <= 3 for v in depths.values()), str(depths))

# ---------- 3. 递归细化盒数（更多面/局部结构） ----------
class FakeE:
    pos = (10.0, 1.5, 10.0)
    category = "wolf"
fake = FakeE()
color = (120, 60, 40)
b0 = entity_boxes(fake, 0, (1.0, 0.0), color)
b1 = entity_boxes(fake, 1, (1.0, 0.0), color)
b2 = entity_boxes(fake, 2, (1.0, 0.0), color)
b3 = entity_boxes(fake, 3, (1.0, 0.0), color)
check("depth0 single cube", len(b0) == 1, str(len(b0)))
check("depth1 body+head+legs", len(b1) == 6, str(len(b1)))
check("depth2 more faces/parts", len(b2) > len(b1), str(len(b2)))
check("depth3 most detail", len(b3) > len(b2), f"{len(b2)}->{len(b3)}")
# 朝向：头在 facing 方向（+x 朝右 → 头盒 cx > 身体 cx）
head = max(b1, key=lambda b: b[3])   # 头通常最大? 用位置判断：facing +x 时头部盒 cx 最大
max_cx = max(b[0] for b in b1)
body_cx = b1[0][0]
check("head oriented toward facing", max_cx > body_cx,
      f"max_cx={max_cx:.2f} body_cx={body_cx:.2f}")

# ---------- 4. 朝向辅助（朝目标） ----------
gen2 = WorldGenerator(size=24, seed=42)
spec2 = parse_scene("森林里有狼追兔子", 24)
loop2 = gen2.build_world(spec2)
wolf = next(eid for eid, e in loop2.world.entities.items() if e.category == "wolf")
rabbit = next(eid for eid, e in loop2.world.entities.items() if e.category == "rabbit")
loop2.world.entities[wolf].goal = rabbit
f = _facing(loop2.world, wolf)
expected = (loop2.world.entities[rabbit].pos[0] - loop2.world.entities[wolf].pos[0],
            loop2.world.entities[rabbit].pos[2] - loop2.world.entities[wolf].pos[2])
check("facing toward goal", (f[0] > 0) == (expected[0] > 0)
      and (f[1] > 0) == (expected[1] > 0), f"f={f} exp={expected}")

# ---------- 5. 注意力渲染：细节增加 + 确定性 ----------
r0 = gen2.generate_image("森林里有狼追兔子", size=420, run_ticks=6, attention=False)
r1 = gen2.generate_image("森林里有狼追兔子", size=420, run_ticks=6, attention=True)
from PIL import Image
im0 = Image.open(io.BytesIO(r0["image"])).convert("RGB")
im1 = Image.open(io.BytesIO(r1["image"])).convert("RGB")
c0 = len(im0.getcolors(maxcolors=100000) or [])
c1 = len(im1.getcolors(maxcolors=100000) or [])
check("attention adds detail (more colors)", c1 >= c0, f"{c0}->{c1}")
diff = sum(1 for x in range(0, 420, 3) for y in range(0, 420, 3)
           if im0.getpixel((x, y)) != im1.getpixel((x, y)))
check("attention changes render", diff > 20, str(diff))
r1b = gen2.generate_image("森林里有狼追兔子", size=420, run_ticks=6, attention=True)
check("attention render deterministic", r1["image"] == r1b["image"], "")
check("attention depths recorded", "attention" in r1 and len(r1["attention"]) == 2,
      str(r1.get("attention")))

print(f"\nATTENTION result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
