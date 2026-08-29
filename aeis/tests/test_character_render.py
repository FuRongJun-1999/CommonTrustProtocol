# -*- coding: utf-8 -*-
"""test_character_render · 里程碑4.8 语义还原角色测试（感知→语义→生成闭环）"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.character_render import (render_character, render_character_png,
                                            spec_from_decomposition, reconstruct_character)
from aeis.game_web.semantics import part_decompose
from PIL import Image

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---------- 1. 渲染确定性 + 有效输出 ----------
spec = {"hair_color": "pink", "ears": True, "eyes": 2, "mouth": True,
        "bowtie_color": "blue", "torso_color": "lightgray",
        "chest_prominent": True, "legs": 2}
png1 = render_character_png(spec)
png2 = render_character_png(spec)
check("render deterministic", png1 == png2, "")
img = Image.open(io.BytesIO(png1))
check("render valid", img.size == (240, 360) and len(png1) > 800, str(img.size))
colors = img.convert("RGB").getcolors(maxcolors=100000)
check("render has content", len(colors or []) >= 4, str(len(colors) if colors else 0))

# ---------- 2. spec 转换（感知 → 生成规格） ----------
decomp = {"hair": {"color_class": "pink", "ears": True},
          "face": {"eyes": [1, 2], "mouth": [1],
                   "bowtie": {"color_class": "blue"}},
          "torso": {"color_class": "lightgray", "chest_prominent": True},
          "legs": [{"side": "left"}, {"side": "right"}]}
s = spec_from_decomposition(decomp)
check("spec ears", s.get("ears") is True, str(s))
check("spec bowtie blue", s.get("bowtie_color") == "blue", str(s))
check("spec chest", s.get("chest_prominent") is True, str(s))
check("spec legs 2", s.get("legs") == 2, str(s))
check("spec eyes >= 2", s.get("eyes") >= 2, str(s))

# ---------- 3. 往返闭环：真实图 1.png → 还原 → 再分解 → 特征一致 ----------
path = r"D:\Program Files\2_ai\demos\1.png"
if os.path.isfile(path):
    img2 = Image.open(path).convert("RGBA")
    bg2 = Image.new("RGBA", img2.size, (255, 255, 255, 255))
    com = Image.alpha_composite(bg2, img2).convert("RGB")
    b2 = io.BytesIO(); com.save(b2, format="PNG")
    r = reconstruct_character(b2.getvalue(), size=320)
    check("reconstruct ok", r["ok"] is True, "")
    spec2 = r["spec"]
    check("hair detected", "hair_color" in spec2, str(spec2))
    check("eyes >= 2", spec2.get("eyes", 0) >= 2, str(spec2))
    check("bowtie detected", "bowtie_color" in spec2, str(spec2))
    check("torso detected", "torso_color" in spec2, str(spec2))
    check("legs detected", spec2.get("legs", 0) >= 1, str(spec2))
    check("summary readable", len(r["summary"]) > 10, "")
    # 还原图再分解：核心特征保持（人物/头/躯干/腿）
    rd = part_decompose(r["image"], size=260)
    check("roundtrip hair", rd.get("hair") is not None, str(rd.get("hair")))
    check("roundtrip face", rd.get("face") is not None, "")
    check("roundtrip torso", rd.get("torso") is not None, str(rd.get("torso")))
    check("roundtrip legs", len(rd.get("legs", [])) >= 1, str(rd.get("legs")))

print(f"\nCHARACTER result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
