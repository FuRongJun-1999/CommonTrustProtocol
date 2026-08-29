# -*- coding: utf-8 -*-
"""test_semantics_real · 真实图像语义描述测试（通用色彩分类）"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web import semantics as S
from PIL import Image, ImageDraw

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 1. 通用色彩分类 ----------
check("white", S.classify_color((255, 255, 255)) == "white", "")
check("skin warm", S.classify_color((240, 200, 180)) == "skin", S.classify_color((240, 200, 180)))
check("black", S.classify_color((20, 20, 25)) == "black", "")
check("green", S.classify_color((60, 180, 80)) == "green", "")
check("blue", S.classify_color((40, 90, 220)) == "blue", S.classify_color((40, 90, 220)))
check("red", S.classify_color((220, 60, 50)) in ("red", "orange"), "")

# ---------- 2. 合成人物图（肤色脸+黑发+红上衣+白背景） → 描述 ----------
img = Image.new("RGB", (200, 300), (255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([50, 150, 150, 290], fill=(200, 60, 50))      # 红上衣
d.ellipse([70, 60, 130, 130], fill=(240, 200, 180))       # 肤色脸
d.ellipse([72, 30, 128, 75], fill=(25, 25, 30))           # 黑发
buf = io.BytesIO(); img.save(buf, format="PNG")
desc = S.describe_image(buf.getvalue(), size=200)
cl = desc["classes"]
check("desc produced", len(desc["description"]) > 10, "")
check("skin class found", "skin" in cl, str(cl.keys()))
check("red class found", "red" in cl, str(cl.keys()))
check("black hair found", "black" in cl, str(cl.keys()))
check("subject red dominant", "red" in cl, str(cl.keys()))  # 背景白被 bg 排除
# 肤色区域位于中部偏上（脸）
if "skin" in cl:
    cy = cl["skin"]["centers"][0][1]
    check("face in upper area", cy < 0.6, str(cy))

# ---------- 3. 真实人物图（1.png）→ 描述可生成 ----------
path = r"D:\Program Files\2_ai\demos\1.png"
if os.path.isfile(path):
    img2 = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", img2.size, (255, 255, 255, 255))
    com = Image.alpha_composite(bg, img2).convert("RGB")
    b2 = io.BytesIO(); com.save(b2, format="PNG")
    d2 = S.describe_image(b2.getvalue(), size=280)
    check("real image described", len(d2["description"]) > 20, d2["description"][:80])
    check("real image has classes", len(d2["classes"]) >= 3, str(list(d2["classes"].keys())[:8]))

print(f"\nSEMREAL result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
