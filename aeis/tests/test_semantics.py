# -*- coding: utf-8 -*-
"""test_semantics · 里程碑4.5 图像语义提取测试
（轮廓/形状/颜色/亮度 → 从外到内 → 图的信息定义；生成-感知闭环）"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web import semantics as S
from aeis.game_web.generate import WorldGenerator
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

def make_png(size=160):
    img = Image.new("RGB", (size, size), (24, 34, 46))
    d = ImageDraw.Draw(img)
    d.rectangle([20, 20, 90, 90], fill=(120, 60, 40))       # 外方块 wolf
    d.ellipse([45, 45, 65, 65], fill=(235, 230, 230))       # 内圆 rabbit
    d.polygon([(120, 30), (150, 30), (135, 60)], fill=(58, 125, 58))  # 三角 leaf
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

png = make_png()
g = S.analyze_image(png, size=160, levels=2)
nodes = g["nodes"]

# ---------- 1. 从外到内：包含边（内部结构挂在外部结构下） ----------
inside_edges = [e for e in g["edges"] if e["relation"] == "inside"]
check("hierarchy: inside edge found", len(inside_edges) >= 1, str(g["edges"]))
check("hierarchy: level2 node has parent", any(n["level"] == 2 and n["parent"]
      for n in nodes), str([(n["id"], n["level"], n["parent"]) for n in nodes]))
# 内圆（white）应作为外部方块（wolf 棕）的内部结构
white_inside = [n for n in nodes if n["level"] == 2 and n["label"] in ("rabbit", "sheep")]
check("inner circle inside outer square", len(white_inside) >= 1,
      str([(n["id"], n["label"], n["parent"]) for n in white_inside]))

# ---------- 2. 形状分类（宽高比/填充率/圆形度） ----------
wolf = next(n for n in nodes if n["label"] == "wolf" and n["level"] == 1)
leaf = next(n for n in nodes if n["label"] == "leaf")
check("square high fill", wolf["shape"]["fill"] > 0.7, str(wolf["shape"]))
check("triangle lower fill", leaf["shape"]["fill"] < 0.7, str(leaf["shape"]))
white = next(n for n in nodes if n["label"] in ("rabbit", "sheep") and n["level"] == 1)
check("circle circularity high", white["shape"]["circularity"] > 1.0,
      str(white["shape"]))

# ---------- 3. 亮度区分 ----------
dark = min(nodes, key=lambda n: n["luminance"])
bright = max(nodes, key=lambda n: n["luminance"])
check("brightness separates", bright["luminance"] - dark["luminance"] > 50,
      f"{dark['luminance']} vs {bright['luminance']}")
check("white bright", white["luminance"] > 150, str(white["luminance"]))

# ---------- 4. 确定性 ----------
g2 = S.analyze_image(png, size=160, levels=2)
check("deterministic graph", g["summary"] == g2["summary"], "")
check("deterministic nodes", len(g["nodes"]) == len(g2["nodes"]), "")

# ---------- 5. 生成-感知闭环：文字生图 → 提取语义 → 匹配源头场景 ----------
gen = WorldGenerator(size=24, seed=42)
r = gen.generate_image("森林里有狼追兔子，湖边有一只守卫", size=420, run_ticks=6)
gr = S.analyze_image(r["image"], size=320)
labels = [n["label"] for n in gr["nodes"] if n["level"] == 1]
check("roundtrip: brown predator/trunk present",
      any(l in ("wolf", "trunk") for l in labels), str(labels))
check("roundtrip: water present", "water" in labels, str(labels))
check("roundtrip: leaf present", "leaf" in labels, str(labels))
check("roundtrip: white animal present",
      any(l in ("rabbit", "sheep") for l in labels), str(labels))
check("roundtrip: guard/player present",
      any(l in ("guard", "player") for l in labels), str(labels))

# ---------- 6. 可读描述（图的信息定义） ----------
check("summary readable", len(g["summary"]) > 20 and "图 =" in g["summary"],
      g["summary"][:80])

print(f"\nSEMANTICS result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
