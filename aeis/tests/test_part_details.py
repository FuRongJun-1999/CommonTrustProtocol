# -*- coding: utf-8 -*-
"""test_part_details · 里程碑4.7 部件细节化测试（角色验证迭代）
（兔耳发饰/蝴蝶结/胸廓突出/躯干主色众数——真实图反馈驱动的修正）"""
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

# ---------- 1. 色彩分类：蓝/青边界 ----------
check("blue stays blue", S.classify_color((40, 90, 220)) == "blue",
      S.classify_color((40, 90, 220)))
check("cyan stays cyan", S.classify_color((60, 200, 210)) == "cyan",
      S.classify_color((60, 200, 210)))
check("dark gray-black", S.classify_color((25, 25, 30)) == "black", "")

# ---------- 2. 合成人物：黑发+兔耳尖+肤色脸带眼口+蓝蝴蝶结+白上衣 ----------
img = Image.new("RGB", (200, 300), (255, 255, 255))
d = ImageDraw.Draw(img)
# 兔耳（两根上凸粉色尖）
d.polygon([(80, 60), (86, 25), (92, 60)], fill=(240, 150, 180))   # 左耳
d.polygon([(108, 60), (114, 25), (120, 60)], fill=(240, 150, 180)) # 右耳
d.rectangle([72, 58, 128, 88], fill=(240, 150, 180))              # 发
d.ellipse([72, 86, 128, 140], fill=(240, 200, 180))               # 脸
d.ellipse([88, 104, 96, 112], fill=(30, 25, 25))                  # 左眼
d.ellipse([104, 104, 112, 112], fill=(30, 25, 25))                # 右眼
d.ellipse([96, 122, 104, 128], fill=(120, 40, 40))                # 口
# 蓝蝴蝶结（两瓣+结）在脖子
d.polygon([(86, 148), (78, 142), (86, 140)], fill=(40, 90, 220))
d.polygon([(94, 148), (102, 142), (94, 140)], fill=(40, 90, 220))
d.rectangle([88, 140, 92, 144], fill=(40, 90, 220))               # 结
d.rectangle([94, 144, 106, 170], fill=(240, 200, 180))            # 脖子
# 白上衣（带灰阴影模拟白衣——白衣必须与纯白背景可分，靠阴影/明暗）
d.rectangle([50, 168, 150, 290], fill=(226, 228, 233))
d.rectangle([55, 175, 145, 285], fill=(203, 208, 218))            # 阴影
buf = io.BytesIO(); img.save(buf, format="PNG")
r = S.part_decompose(buf.getvalue(), size=200)

check("person detected", r.get("person") is not None, "")
check("head found", r["head"] is not None, "")
check("hair pink", r["hair"] is not None and r["hair"]["color_class"] == "pink",
      str(r["hair"]))
check("rabbit ears", r["hair"] is not None and r["hair"].get("ears") is True,
      str(r["hair"].get("ear_columns")))
check("face found", r["face"] is not None, "")
check("bowtie blue", r["face"] is not None and r["face"].get("bowtie")
      and r["face"]["bowtie"]["color_class"] == "blue",
      str(r["face"].get("bowtie") if r["face"] else None))
check("torso lightgray (white outfit)", r["torso"] is not None
      and r["torso"]["color_class"] in ("lightgray", "white"),
      str(r["torso"]))
check("description mentions ears/bowtie", "兔耳" in r["description"]
      and "蝴蝶结" in r["description"], r["description"][:80])

# ---------- 3. 真实图 1.png：对齐用户描述 ----------
path = r"D:\Program Files\2_ai\demos\1.png"
if os.path.isfile(path):
    img2 = Image.open(path).convert("RGBA")
    bg2 = Image.new("RGBA", img2.size, (255, 255, 255, 255))
    com = Image.alpha_composite(bg2, img2).convert("RGB")
    b2 = io.BytesIO(); com.save(b2, format="PNG")
    rr = S.part_decompose(b2.getvalue(), size=320)
    check("real: pink hair", rr["hair"] is not None
          and rr["hair"]["color_class"] in ("pink", "red"), str(rr["hair"]))
    check("real: rabbit ears", rr["hair"] is not None and rr["hair"].get("ears") is True,
          str(rr["hair"].get("ear_columns")))
    check("real: blue bowtie", rr["face"] is not None and rr["face"].get("bowtie")
          and rr["face"]["bowtie"]["color_class"] in ("blue", "cyan"),
          str(rr["face"].get("bowtie") if rr["face"] else None))
    check("real: light torso (white outfit)", rr["torso"] is not None
          and rr["torso"]["color_class"] in ("lightgray", "white"),
          str(rr["torso"]))

print(f"\nPARTDETAILS result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
