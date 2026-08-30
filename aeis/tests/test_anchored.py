# -*- coding: utf-8 -*-
"""test_anchored · 里程碑4.25 骨架锚定检测（胸对称对 vs 低位区域胸下大簇）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.chest_detect import anchored_lowregion_detect
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

# 合成：肤色底 + 对称局部小簇对(胸) + 下方单个大低位区域簇
img = Image.new("RGB", (200, 200), (235, 215, 210))
d = ImageDraw.Draw(img)
d.ellipse([62, 75, 72, 85], fill=(200, 60, 50))      # 左局部小簇(小)
d.ellipse([128, 75, 138, 85], fill=(200, 60, 50))    # 右局部小簇(小, 对称)
d.ellipse([70, 130, 130, 165], fill=(180, 40, 30))  # 低位区域(大, 下方)
res = anchored_lowregion_detect(img, min_n=4)
check("小簇 found", len(res["小簇"]) >= 2, str(res["小簇"]))
# 低位区域 = 下方大簇
g = res["lowregions"][0] if res["lowregions"] else {}
check("lowregion found below chest", g.get("rel_y", 0) > 0.5,
      str(res["lowregions"]))
# 低位区域面积大于局部小簇
if res["小簇"] and res["lowregions"]:
    n_max = max(x["n"] for x in res["小簇"])
    check("lowregion larger than 小簇", res["lowregions"][0]["n"] > n_max,
          "nipple_max=%d lowregion=%d" % (n_max, res["lowregions"][0]["n"]))

# 真实图 1/2
for name in ("1.png", "2.png"):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        '..', '..', 'demos', name)
    if not os.path.isfile(path):
        continue
    im = Image.open(path).convert("RGB")
    w, h = im.size
    ratio = 600.0 / max(w, h)
    an = im.resize((max(1, int(w * ratio)), max(1, int(h * ratio))))
    res2 = anchored_lowregion_detect(an, min_n=6)
    check(name + " has 小簇", len(res2["小簇"]) >= 2,
          str(len(res2["小簇"])))
    check(name + " has lowregion", len(res2["lowregions"]) >= 1,
          str(res2["lowregions"]))
    if name == "4.png":
        # 半身图骨架判定：无低位区域（核心面积小/上部误报排除）
        check("4.png half-body no lowregion", len(res2["lowregions"]) == 0,
              str(res2["lowregions"]))
    if name == "2.png" and res2["小簇"] and res2["lowregions"]:
        # 用户标注校准: 局部小簇=#18/#19(小对称对), 低位区域=#39核心(高饱和收缩)
        nbbox = [n["bbox"] for n in res2["小簇"]]
        check("2.png 小簇 = user #18/#19",
              any(abs(b[0] - 153) < 8 and abs(b[1] - 211) < 8 for b in nbbox)
              and any(abs(b[0] - 264) < 8 and abs(b[1] - 209) < 8 for b in nbbox),
              str(nbbox))
        gc = res2["lowregions"][0]["core"]
        check("2.png lowregion core (user range)",
              abs(gc[0] - 241) < 15 and abs(gc[1] - 343) < 15
              and abs(gc[2] - 269) < 15 and abs(gc[3] - 425) < 15,
              str(gc))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)