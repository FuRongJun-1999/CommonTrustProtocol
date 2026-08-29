# -*- coding: utf-8 -*-
"""test_part_decompose · 里程碑4.6 递归部件分解测试
（图→人物→头{脸/发/眼/口}→躯干→腿；从外到内的部件递归）"""
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

# ---------- 合成人物（白背景 + 黑发 + 肤色脸带眼口 + 红上衣） ----------
img = Image.new("RGB", (200, 300), (255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([72, 26, 128, 58], fill=(25, 25, 30))          # 黑发（脸帽）
d.ellipse([72, 56, 128, 118], fill=(240, 200, 180))        # 肤色脸
d.ellipse([88, 84, 96, 92], fill=(30, 25, 25))             # 左眼
d.ellipse([104, 84, 112, 92], fill=(30, 25, 25))           # 右眼
d.ellipse([96, 102, 104, 108], fill=(120, 40, 40))         # 口
d.rectangle([94, 118, 106, 152], fill=(240, 200, 180))     # 脖子
d.rectangle([50, 150, 150, 290], fill=(200, 60, 50))       # 红上衣
buf = io.BytesIO(); img.save(buf, format="PNG")
r = S.part_decompose(buf.getvalue(), size=200)

check("person detected", r.get("person") is not None, str(r.keys()))
check("head found", r["head"] is not None, "")
check("face found (skin)", r["face"] is not None, "")
check("hair found black", r["hair"] is not None
      and r["hair"]["color_class"] == "black", str(r["hair"]))
check("eyes detected", r["face"] and r["face"].get("eyes") and len(r["face"]["eyes"]) >= 1,
      str(r["face"].get("eyes") if r["face"] else None))
check("mouth detected", r["face"] and r["face"].get("mouth") and len(r["face"]["mouth"]) >= 1,
      str(r["face"].get("mouth") if r["face"] else None))
check("torso red", r["torso"] is not None and r["torso"]["color_class"] == "red",
      str(r["torso"]))
check("legs detected", len(r["legs"]) >= 1, str([l["side"] for l in r["legs"]]))
check("description readable", len(r["description"]) > 10, r["description"][:60])

# 层次：face 在 head 内部（bbox 包含）
if r["face"] and r["head"]:
    fb = r["face"]["bbox"]; hb = r["head"]["bbox"]
    check("face inside head", fb[0] >= hb[0] - 2 and fb[2] <= hb[2] + 2
          and fb[3] <= hb[3] + 2, f"face={fb} head={hb}")

# ---------- 确定性 ----------
r2 = S.part_decompose(buf.getvalue(), size=200)
check("deterministic", r["description"] == r2["description"], "")

# ---------- 真实人物图 1.png ----------
path = r"D:\Program Files\2_ai\demos\1.png"
if os.path.isfile(path):
    img2 = Image.open(path).convert("RGBA")
    bg2 = Image.new("RGBA", img2.size, (255, 255, 255, 255))
    com = Image.alpha_composite(bg2, img2).convert("RGB")
    b2 = io.BytesIO(); com.save(b2, format="PNG")
    rr = S.part_decompose(b2.getvalue(), size=280)
    check("real: person+head+face", rr.get("person") and rr["head"] and rr["face"], "")
    check("real: described", len(rr["description"]) > 10, rr["description"][:80])

print(f"\nPARTDECOMP result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
