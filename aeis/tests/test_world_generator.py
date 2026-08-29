# -*- coding: utf-8 -*-
"""test_world_generator · 里程碑4.3 文字生图/文字生视频测试
（场景解析/世界实例化/确定性/PNG 有效性/GIF 多帧且实体移动）"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.generate import WorldGenerator, parse_scene

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 1. 场景解析 ----------
spec = parse_scene("森林里有狼追兔子")
check("terrain trees", spec["trees"] == 3, str(spec))
check("two entities", len(spec["entities"]) == 2, str(spec["entities"]))
wolf = spec["entities"][0]
rabbit = spec["entities"][1]
check("wolf seek rabbit", wolf["category"] == "wolf" and wolf["behavior"] == "seek"
      and wolf["goal"] == "rabbit", str(wolf))
check("rabbit wander (not chaser)", rabbit["category"] == "rabbit"
      and rabbit["behavior"] == "wander", str(rabbit))

spec2 = parse_scene("湖边有守卫巡逻，草地上羊在闲逛")
check("lake water", spec2["water"] is True, str(spec2))
check("multi-scene entities", len(spec2["entities"]) == 2
      and {e["category"] for e in spec2["entities"]} == {"guard", "sheep"}, str(spec2))

# ---------- 2. 世界实例化 ----------
gen = WorldGenerator(size=24, seed=42)
loop = gen.build_world(spec)
check("world entities", len(loop.world.entities) == 2, str(loop.world.entities.keys()))
goal_ok = any(e.behavior == "seek" and e.goal
              for e in loop.world.entities.values())
check("goal resolved", goal_ok, str([(e.category, e.goal) for e in loop.world.entities.values()]))

loop2 = gen.build_world(parse_scene("有一名守卫在巡逻"))
check("follow gets patrol path", any(e.behavior == "follow" and e.goal == "patrol"
                                     for e in loop2.world.entities.values()),
      str([(e.category, e.behavior, e.goal) for e in loop2.world.entities.values()]))

# ---------- 3. 文字生图 ----------
img = gen.generate_image("森林里有狼追兔子，湖边有一只守卫", size=480, run_ticks=3)
check("image bytes", img["image"][:8] == b"\x89PNG\r\n\x1a\n" and len(img["image"]) > 5000,
      str(len(img["image"])))
img2 = gen.generate_image("森林里有狼追兔子，湖边有一只守卫", size=480, run_ticks=3)
check("image deterministic", img["image"] == img2["image"], "")
check("image summary", "森林" in img["summary"] or "实体" in img["summary"], img["summary"])

# ---------- 4. 文字生视频 ----------
vid = gen.generate_video("森林里狼追兔子", ticks=10, fps=4, size=240)
check("gif header", vid["gif"][:6] == b"GIF89a", str(vid["gif"][:6]))
check("gif frames", vid["frames"] == 10, str(vid["frames"]))
check("gif bytes", len(vid["gif"]) > 3000, str(len(vid["gif"])))
vid2 = gen.generate_video("森林里狼追兔子", ticks=10, fps=4, size=240)
check("video deterministic", vid["gif"] == vid2["gif"], "")
check("world evolved", vid["final_tick"] == 10, str(vid["final_tick"]))

# 视频帧间实体移动（世界演化=时序生成）
from PIL import Image
gif = Image.open(io.BytesIO(vid["gif"]))
n_frames = getattr(gif, "n_frames", 1)
gif.seek(0)
f0 = gif.convert("RGB")
gif.seek(n_frames - 1)
f1 = gif.convert("RGB")
# 逐像素比较（实体移动 → 帧间有差异）
diffs = 0
w, h = f0.size
for x in range(0, w, 4):
    for y in range(0, h, 4):
        if f0.getpixel((x, y)) != f1.getpixel((x, y)):
            diffs += 1
check("video frames differ (world evolved)", diffs > 10,
      f"diff_pixels={diffs} frames={n_frames}")

# ---------- 5. 保存导出 ----------
out = gen.save_image("森林里狼追兔子", r"D:\Program Files\2_ai\CommonTrustProtocol\aeis\tests\_tmp_gen.png")
check("save image", os.path.isfile(out["path"]) and os.path.getsize(out["path"]) > 5000, "")
out2 = gen.save_video("森林里狼追兔子", ticks=6, fps=3, size=200,
                      path=r"D:\Program Files\2_ai\CommonTrustProtocol\aeis\tests\_tmp_gen.gif")
check("save video", os.path.isfile(out2["path"]) and os.path.getsize(out2["path"]) > 2000, "")

print(f"\nWORLDGEN result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
