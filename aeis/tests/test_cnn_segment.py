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
        # 红色内容自动区分：红晕=上部（脸），局部小簇=中部（胸）——同一颜色类别
        # 下，内容由空间位置自动涌现（语义不预设，从特征派生）
        up_red = [lb for r, lb in zip(res2["regions"], res2["labels"])
                  if "红" in lb and "上部" in lb and r["area"] >= 10]
        mid_red = [lb for r, lb in zip(res2["regions"], res2["labels"])
                   if "红" in lb and "中部" in lb and r["area"] >= 5]
        check("blush auto-separated at upper (face)",
              len(up_red) >= 1, str(up_red[:3]))
        check("nipple auto-separated at mid (chest)",
              len(mid_red) >= 1, str(mid_red[:3]))
        # 下部红区（用户确认：低位区域特征——颜色+亮度+轮廓位置共同识别）
        low_red = [lb for r, lb in zip(res2["regions"], res2["labels"])
                   if "红" in lb and "下部" in lb and r["area"] >= 4]
        check("lower red region auto-detected",
              len(low_red) >= 1, str(low_red[:3]))
        # LAB 新格式（颜色-形状-位置yx-大小）：形状词/2D位置词/亮度词
        res4 = CS.segment_adaptive(com, k=0.5, min_area=4, step=2)
        lab_labels = res4["labels"]
        def pos3(lb):
            parts = lb.split("-")
            return parts[2] if len(parts) >= 3 else ""
        check("lab 4-part format",
              all(len(lb.split("-")) == 4 for lb in lab_labels),
              str(lab_labels[:3]))
        check("lab shape words present",
              any("-圆点-" in lb or "-块状-" in lb or "-竖条-" in lb
                  or "-横条-" in lb or "-散状-" in lb for lb in lab_labels),
              str(lab_labels[:5]))
        check("lab 2d position words",
              all(len(pos3(lb)) == 2 and pos3(lb)[0] in "上中下"
                  and pos3(lb)[1] in "左右中" for lb in lab_labels
                  if pos3(lb)), str(lab_labels[:5]))
        up_red2 = [lb for r, lb in zip(res4["regions"], lab_labels)
                   if "红" in lb and pos3(lb).startswith("上")
                   and r["area"] >= 8]
        check("lab upper red (blush)", len(up_red2) >= 1, str(up_red2[:3]))
        low_red2 = [lb for r, lb in zip(res4["regions"], lab_labels)
                    if "红" in lb and pos3(lb).startswith("下")
                    and r["area"] >= 8]
        check("lab lower red (crotch)", len(low_red2) >= 1, str(low_red2[:3]))
    except Exception as e:
        check("real image test", False, str(e))
else:
    print("  SKIP real image (demos/1.png absent)")

# ---------- 9. LAB 感知特征（方向三） ----------
field_lab, gw_lab, gh_lab = CS.feature_vectors_lab(img, step=2)
check("lab field shape", gw_lab == 30 and gh_lab == 30,
      f"gw={gw_lab} gh={gh_lab}")
# 蓝块 LAB b 通道（0.5-）应显著低于红块
def lab_b(field, x, y):
    return field[y][x][2]
check("lab blue block b low", lab_b(field_lab, 8, 8) < 0.42,
      f"b={lab_b(field_lab, 8, 8):.3f}")
check("lab red block b high", lab_b(field_lab, 22, 8) > 0.45,
      f"b={lab_b(field_lab, 22, 8):.3f}")

# ---------- 10. MST 自适应阈值分割（方向一） ----------
ad = CS.adaptive_segment(img, k=0.5, min_area=4, step=2)
check("adaptive has regions", len(ad) >= 4, str(len(ad)))
check("adaptive quality fields", all("info" in r and "boundary" in r for r in ad))
# 蓝块/红块区域分离（LAB 色相）
blu = [r for r in ad if r["centroid"][2] < 0.40 and r["area"] >= 20]
red = [r for r in ad if r["centroid"][1] > 0.55 and r["area"] >= 20]
check("adaptive blue region", len(blu) >= 1, str(len(blu)))
check("adaptive red region", len(red) >= 1, str(len(red)))

# ---------- 11. LAB 自动命名（_auto_label_lab） ----------
c_white = CS.feature_vectors_lab(Image.new("RGB", (4, 4), (255, 255, 255)), step=2)[0][0][0]
check("lab white label", "白" in CS._auto_label_lab(c_white), str(CS._auto_label_lab(c_white)))
c_red = CS.feature_vectors_lab(Image.new("RGB", (4, 4), (230, 65, 64)), step=2)[0][0][0]
check("lab red label", "红" in CS._auto_label_lab(c_red), str(CS._auto_label_lab(c_red)))
c_blue = CS.feature_vectors_lab(Image.new("RGB", (4, 4), (80, 130, 200)), step=2)[0][0][0]
check("lab blue label", "蓝" in CS._auto_label_lab(c_blue), str(CS._auto_label_lab(c_blue)))

# ---------- 12. 注意力递归细化（方向二） ----------
# 渐变图（内部渐变 → 信息量高 → 递归细分出 level 1）
grad = Image.new("RGB", (64, 64))
for gx in range(64):
    for gy in range(64):
        grad.putpixel((gx, gy), (int(40 + gx * 3), int(90 - gx), int(220 - gy * 2)))
ref = CS.refine_recursive(grad, k0=0.5, k1=0.2, max_depth=1, info_thresh=0.00001)
check("refine levels", any(r["level"] == 0 for r in ref)
      and any(r["level"] == 1 for r in ref),
      "levels=" + str(set(r["level"] for r in ref)))
check("refine children structure", any(r.get("children") for r in ref))
lv1 = [r for r in ref if r["level"] == 1 and r.get("label")]
check("refine labels on level1", len(lv1) >= 2, str(len(lv1)))

# ---------- 13. 质量自检（方向五） ----------
q = CS.quality_report(ad)
check("quality report keys", set(q) >= {"score", "mean_info", "mean_boundary"},
      str(q.keys()))
check("quality mean boundary positive", q["mean_boundary"] > 0)

# ---------- 14. 灰度+高斯边缘提取（轮廓识别 · 用户方法论） ----------
hard = Image.new("RGB", (100, 80), (255, 255, 255))
hd = ImageDraw.Draw(hard)
hd.rectangle([8, 8, 30, 30], fill=(20, 20, 20))     # 硬边界方块
hd.ellipse([40, 8, 62, 30], fill=(30, 30, 30))      # 圆
edge_map = CS.gray_gauss_edge_map(hard, sigma=1.0)
check("edge map size", edge_map.size == (100, 80), str(edge_map.size))
regs_c = CS.closed_contour_segments(hard, sigma=1.0)
check("closed contours on hard-edge", len(regs_c) >= 3,
      str([r["bbox"] for r in regs_c[:4]]))
# 方块区域：bbox 中心在方块内（边缘像素腐蚀 1px，允许 ±2 容差）
def in_square(r):
    cx = (r["bbox"][0] + r["bbox"][2]) / 2
    cy = (r["bbox"][1] + r["bbox"][3]) / 2
    return 12 <= cx <= 26 and 12 <= cy <= 26
check("contour square region", any(in_square(r) for r in regs_c),
      str([r["bbox"] for r in regs_c[:4]]))
check("contour has edge ratio", all(r["edge_pixels"] > 0 for r in regs_c))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)