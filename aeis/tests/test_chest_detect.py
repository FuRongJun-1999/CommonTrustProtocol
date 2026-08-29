# -*- coding: utf-8 -*-
"""test_chest_detect · 里程碑4.19 胸廓特征提取（局部小簇/覆盖带/胸廓区域）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.chest_detect import 小簇, bra_band, chest_features, chest_arcs
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

# 合成：肤色底 + 两个红色局部小簇(对称) + 暗色覆盖带
img = Image.new("RGB", (200, 200), (235, 215, 210))     # 肤色底
d = ImageDraw.Draw(img)
d.rectangle([0, 100, 200, 140], fill=(90, 70, 80))      # 覆盖带暗带
d.ellipse([60, 130, 80, 150], fill=(200, 60, 50))       # 左局部小簇
d.ellipse([120, 130, 140, 150], fill=(200, 60, 50))     # 右局部小簇
d.ellipse([85, 30, 105, 50], fill=(240, 130, 120))      # 上部红晕(应排除)

nps = 小簇(img)
check("小簇 found", len(nps) >= 2, str([n["bbox"] for n in nps]))
# 局部小簇在胸廓(rel_y 0.35+)而非上部红晕
low = [n for n in nps if n["rel_y"] > 0.35]
check("小簇 at chest position", len(low) >= 2,
      str([(n["bbox"], n["rel_y"]) for n in nps]))
bands = bra_band(img)
check("bra band found", len(bands) >= 1, str(bands))
f = chest_features(img)
check("nipple pair detected", len(f["nipple_pairs"]) >= 1,
      str(f["nipple_pairs"]))
check("chest regions", len(f["chest_regions"]) >= 1,
      str([c["bbox"] for c in f["chest_regions"]]))

# ---------- 弧检测（半圆弧轮廓） ----------
# 合成：肤色底 + 半圆弧（胸廓）
arc_img = Image.new("RGB", (120, 100), (235, 215, 210))
ad = ImageDraw.Draw(arc_img)
# 下凸半圆弧：弧底 y=70，两端 y=50，宽 80
import math as _m
for x in range(20, 101):
    # 半圆 (x-60)^2 + (y-70)^2 = 40^2, 取下半 y=70+sqrt(...)
    d2 = 1600 - (x - 60) ** 2
    if d2 >= 0:
        y = int(70 + _m.sqrt(d2) * 0.6)     # 扁弧（宽>高）
        ad.point((x, y), fill=(150, 90, 100))
        ad.point((x, y + 1), fill=(150, 90, 100))
arcs = chest_arcs(arc_img)
check("chest arc detected", len(arcs) >= 1,
      str([a["bbox"] for a in arcs[:3]]))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)