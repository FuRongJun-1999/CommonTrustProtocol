# -*- coding: utf-8 -*-
"""test_semantics_masks · 里程碑4.10 精确语义掩膜/轮廓/深度递归测试"""
import os, sys, io, base64
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

# ---------- 1. 掩膜与轮廓 ----------
img = Image.new("RGB", (200, 300), (255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([50, 50, 150, 250], fill=(226, 228, 233))       # 大矩形
buf = io.BytesIO(); img.save(buf, format="PNG")
im = img.resize((200, 200))
mask = S.mask_from_bbox(im, (50, 50, 150, 150),
                        lambda c, x, y: c[0] < 250, scale=2)
check("mask png non-empty", len(mask) > 200, str(len(mask)))
mim = Image.open(io.BytesIO(mask)).convert("L")
check("mask has white pixels", any(mim.getpixel((x, y)) == 255
                                   for x in range(0, mim.size[0], 8)
                                   for y in range(0, mim.size[1], 8)), "")
rows = [[1 if (50 <= x <= 150 and 50 <= y <= 150) else 0
         for x in range(50, 151)] for y in range(50, 151)]
poly = S.boundary_polygon(rows, (50, 50, 150, 150), max_pts=20)
check("boundary polygon", len(poly) >= 8, str(len(poly)))
check("polygon on boundary", all(49 <= p[0] <= 151 and 49 <= p[1] <= 151
                                 for p in poly), str(poly[:3]))

# ---------- 2. 胸廓子内容（深度递归：局部小簇/晕环 + 覆盖带） ----------
img2 = Image.new("RGB", (200, 200), (255, 255, 255))
d2 = ImageDraw.Draw(img2)
d2.rectangle([72, 6, 128, 30], fill=(25, 25, 30))          # 发
d2.ellipse([72, 24, 128, 70], fill=(240, 200, 180))        # 脸
d2.rectangle([94, 62, 106, 70], fill=(240, 200, 180))      # 脖子
d2.rectangle([50, 67, 150, 193], fill=(226, 228, 233))     # 躯干
d2.ellipse([82, 93, 94, 101], fill=(150, 70, 90))          # 左局部小簇/晕环
d2.ellipse([106, 93, 118, 101], fill=(150, 70, 90))        # 右局部小簇/晕环
d2.rectangle([50, 85, 150, 89], fill=(160, 90, 160))       # 覆盖带
buf2 = io.BytesIO(); img2.save(buf2, format="PNG")
im2 = img2.convert("RGB")
w2, h2 = im2.size
data2 = list(im2.getdata())
border2 = []
for x in range(w2): border2 += [data2[x], data2[(h2-1)*w2+x]]
for y in range(h2): border2 += [data2[y*w2], data2[y*w2+w2-1]]
q2 = {}
for c in border2:
    k = (c[0]//24, c[1]//24, c[2]//24); q2[k] = q2.get(k,0)+1
k2 = max(q2, key=q2.get); bgrgb = (k2[0]*24+12, k2[1]*24+12, k2[2]*24+12)
fgm = S._fg_mask(im2, bgrgb)
dets = S.chest_details(im2, fgm, (50, 67, 150, 193))
kinds = [dd["class"] for dd in dets]
check("nipple/areola detected", "nipple/areola" in kinds, str(kinds))
check("bra band detected", "bra" in kinds, str(kinds))
小簇 = [dd for dd in dets if dd["class"] == "nipple/areola"]
if len(小簇) >= 2:
    check("小簇 symmetric", abs(小簇[0]["position"][1] - 小簇[1]["position"][1]) < 8
          and abs(小簇[0]["position"][0] - 小簇[1]["position"][0]) > 5,
          str([n["position"] for n in 小簇]))

# ---------- 3. 深度递归（decompose_masks：躯干 children） ----------
r = S.decompose_masks(buf2.getvalue(), size=200)
torso = next((r["regions"][i] for i in range(len(r["regions"]))
              if r["regions"][i]["semantic"] == "躯干"), None)
check("torso with children", torso is not None and len(torso.get("children", [])) >= 2,
      str([c["semantic"] for c in torso["children"]] if torso else None))
check("children have masks", torso is not None and all(len(c["mask_b64"]) > 100
      for c in torso.get("children", [])), "")

# ---------- 4. 真实图 1.png：掩膜/轮廓/胸廓细节 ----------
path = r"D:\Program Files\2_ai\demos\1.png"
if os.path.isfile(path):
    img3 = Image.open(path).convert("RGBA")
    bg3 = Image.new("RGBA", img3.size, (255, 255, 255, 255))
    com = Image.alpha_composite(bg3, img3).convert("RGB")
    b3 = io.BytesIO(); com.save(b3, format="PNG")
    r3 = S.decompose_masks(b3.getvalue(), size=240)
    check("real regions", len(r3["regions"]) >= 5, str(len(r3["regions"])))
    check("real masks", all(len(x["mask_b64"]) > 100 for x in r3["regions"]), "")
    check("real polygons", all(len(x.get("polygon", [])) >= 4 for x in r3["regions"]), "")
    torso3 = next((x for x in r3["regions"] if x["semantic"] == "躯干"), None)
    check("real torso children", torso3 is not None
          and len(torso3.get("children", [])) >= 1,
          str([c["semantic"] for c in torso3["children"]]) if torso3 else None)

print(f"\nMASKS result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
