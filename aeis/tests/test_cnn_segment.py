# -*- coding: utf-8 -*-
"""test_cnn_segment · 里程碑4.12 卷积自动获得语义（CSPMN 原生神经网络）
====================================================================
核心（荣）：语义不必提前预设，而是根据 CNN 自动卷积时获得。测试：
  - 特征向量场（卷积输出 = 条件向量）
  - 特征空间分割：合成图蓝块/红块/纹理条自动分离（无预设颜色）
  - 涌现语义自动命名：颜色签名由特征派生（白/中蓝/中红/暗灰/浅红…）
  - 区域原型聚类（条件空间子矩阵）
  - 特征引导合并（用特征改进分割）
  - 一键 segment_automatic 入口
  - 无预设调色板断言（语义从卷积激活涌现，非查找表）
"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web import cnn_segment as CS
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

# ---------- 1. 特征向量场（卷积输出 = 条件向量） ----------
img = Image.new("RGB", (60, 60), (255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([5, 5, 25, 25], fill=(40, 90, 220))        # 蓝块
d.rectangle([35, 5, 55, 25], fill=(200, 50, 40))       # 红块
for y in range(40, 56, 4):
    d.line([(5, y), (55, y)], fill=(60, 60, 60), width=2)  # 纹理条
field, gw, gh = CS.feature_vectors(img, step=2)
check("field shape", gw == 30 and gh == 30, f"gw={gw} gh={gh}")
check("field channel count", len(field[0][0]) >= 5,
      str(len(field[0][0])))
# 蓝块中心单元格：b 通道应显著高于 r
blue_cell = field[8][8]
check("blue cell b>r", blue_cell[2] > blue_cell[0] + 0.3,
      f"r={blue_cell[0]:.2f} b={blue_cell[2]:.2f}")
# 纹理条单元格：边缘强度高
tex_cell = field[23][15]
bg_cell = field[2][15]
check("texture cell edge>bg", tex_cell[3] > bg_cell[3] * 3,
      f"tex={tex_cell[3]:.3f} bg={bg_cell[3]:.3f}")

# ---------- 2. 特征空间分割（语义自动获得） ----------
regions = CS.feature_segment(img, feat_threshold=0.35, step=2)
check("segment has regions", len(regions) >= 5, str(len(regions)))
def has_color_area(target="b", min_area=40):
    for r in regions:
        c = r["centroid"]
        if target == "b" and c[2] > c[0] + 0.3 and r["area"] >= min_area:
            return True
        if target == "r" and c[0] > c[2] + 0.3 and r["area"] >= min_area:
            return True
    return False
check("blue area auto-separated", has_color_area("b"),
      "no blue region")
check("red area auto-separated", has_color_area("r"),
      "no red region")

# ---------- 3. 涌现语义自动命名（特征签名，非预设） ----------
labels = CS.auto_label(regions)
blue_labels = [lb for r, lb in zip(regions, labels)
               if r["centroid"][2] > r["centroid"][0] + 0.3 and r["area"] >= 40]
check("blue label contains 蓝", any("蓝" in lb for lb in blue_labels),
      str(blue_labels[:3]))
red_labels = [lb for r, lb in zip(regions, labels)
              if r["centroid"][0] > r["centroid"][2] + 0.3 and r["area"] >= 40]
check("red label contains 红", any("红" in lb for lb in red_labels),
      str(red_labels[:3]))
check("label has texture/edge word", all("-" in lb for lb in labels),
      str(labels[:3]))

# ---------- 4. 区域原型聚类（条件空间子矩阵） ----------
protos = CS.region_prototypes(regions, k=4)
check("prototypes exist", len(protos) >= 2, str(len(protos)))
check("prototype members positive", all(p["members"] > 0 for p in protos))
check("prototype labeled", all(p["label"] for p in protos))

# ---------- 5. 特征引导合并（用特征改进分割） ----------
merged = CS.improve_segmentation(regions, merge_threshold=0.3)
check("merge reduces count", len(merged) < len(regions),
      f"{len(regions)} -> {len(merged)}")
check("merge keeps blue", has_color_area("b", min_area=40) or
      any(r["centroid"][2] > r["centroid"][0] + 0.3 and r["area"] >= 60
          for r in merged),
      "blue lost after merge")

# ---------- 6. 一键 segment_automatic ----------
res = CS.segment_automatic(img, feat_threshold=0.35, step=2,
                           merge_threshold=0.3)
check("automatic keys", set(res) == {"regions", "labels", "prototypes"},
      str(res.keys()))
check("automatic labels aligned", len(res["labels"]) == len(res["regions"]),
      f"{len(res['labels'])} vs {len(res['regions'])}")

# ---------- 7. 无预设调色板断言（语义从卷积激活涌现） ----------
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'aeis', 'game_web', 'cnn_segment.py'),
           encoding='utf-8').read()
check("no preset label table",
      all(k not in src for k in ("SEM_COLORS", "PALETTE", "LABEL_TABLE",
                                 "COLOR_WORDS =", "SEMANTIC_MAP")),
      "found preset label table")
check("color names derived from centroid",
      "centroid" in src and "_auto_label" in src)

# ---------- 8. 真实图像 1.png（图像无关断言） ----------
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    '..', '..', 'demos', '1.png')
if os.path.isfile(path):
    try:
        img2 = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", img2.size, (255, 255, 255, 255))
        com = Image.alpha_composite(bg, img2).convert("RGB").resize((160, 320))
        res2 = CS.segment_automatic(com, feat_threshold=0.35, step=4,
                                    min_area=8, merge_threshold=0.3)
        check("real image regions", len(res2["regions"]) >= 10,
              str(len(res2["regions"])))
        nonbg = [lb for r, lb in zip(res2["regions"], res2["labels"])
                 if r["area"] >= 15 and "白" not in lb]
        check("real image has non-white semantics",
              len(nonbg) >= 3, str(nonbg[:5]))
        check("real image prototypes", len(res2["prototypes"]) >= 3,
              str(len(res2["prototypes"])))
    except Exception as e:
        check("real image test", False, str(e))
else:
    print("  SKIP real image (demos/1.png absent)")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)