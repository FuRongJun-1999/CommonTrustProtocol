# -*- coding: utf-8 -*-
"""test_semicircle_match · 里程碑4.21 半圆模板匹配（胸廓轮廓）"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.semicircle_match import (semicircle_points, match_semicircle,
                                            annotate, edge_local)
from PIL import Image, ImageDraw

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  PASS " + name)
    else:
        failed += 1
        print("  FAIL " + name + " " + detail)

# 1. 半圆点采样
pts = semicircle_points(50, 50, 20)
check("semicircle points", len(pts) == 49 and pts[0][0] == 70
      and pts[0][1] == 50 and pts[-1][0] == 30, str(pts[:3]) + "..." + str(pts[-2:]))
check("semicircle lower half", all(p[1] >= 50 for p in pts),
      "points above center: " + str([p for p in pts if p[1] < 50][:3]))

# 2. 合成半圆弧匹配
syn = Image.new("RGB", (160, 120), (235, 215, 210))
d = ImageDraw.Draw(syn)
for x in range(40, 121):
    d2 = 1600 - (x - 80) ** 2
    if d2 >= 0:
        y = int(70 + math.sqrt(d2) * 0.7)
        d.point((x, y), fill=(150, 90, 100))
        d.point((x, y + 1), fill=(150, 90, 100))
res = match_semicircle(syn, coarse_step=4, r_min=12, r_max=50)
check("synthetic match found", len(res["matches"]) >= 1,
      str(res["matches"][:2]))
check("synthetic score > 0.25", res["matches"][0]["score"] > 0.25,
      str(res["matches"][0]["score"] if res["matches"] else None))

# 3. 标注与局部
ann = annotate(syn, res["matches"][:3])
check("annotate", ann.size == syn.size)
crop, eg, _ = edge_local(syn, res["matches"][0]["bbox"])
check("edge_local", crop.size == eg.size and crop.size[0] > 0)

# 4. 真实图（3.png 高分）
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    '..', '..', 'demos', '3.png')
if os.path.isfile(path):
    try:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        ratio = 400.0 / max(w, h)
        an = img.resize((max(1, int(w * ratio)), max(1, int(h * ratio))))
        res3 = match_semicircle(an, coarse_step=6, r_min=16)
        check("real match top score > 0.3",
              res3["matches"][0]["score"] > 0.3 if res3["matches"] else False,
              str(res3["matches"][:2]))
    except Exception as e:
        check("real match", False, str(e))
else:
    print("  SKIP real (demos/3.png absent)")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
