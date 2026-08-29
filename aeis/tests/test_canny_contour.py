# -*- coding: utf-8 -*-
"""test_canny_contour · 里程碑4.18 Canny轮廓提取+断点连接+分层精细"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.canny_contour import (canny_edges, link_breaks,
                                         closed_regions,
                                         hierarchical_contours)
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

# 硬边界合成图：方块 + 圆 + 三角
syn = Image.new("RGB", (100, 80), (255, 255, 255))
d = ImageDraw.Draw(syn)
d.rectangle([8, 8, 30, 30], fill=(20, 20, 20))
d.ellipse([40, 8, 62, 30], fill=(30, 30, 30))
d.polygon([(8, 40), (30, 60), (8, 60)], fill=(40, 40, 40))

# ---------- 1. Canny ----------
edge, W, H = canny_edges(syn, sigma=1.2, p_hi=0.90)
check("canny edges non-empty", len(edge) > 100, str(len(edge)))
check("canny size", W == 100 and H == 80, f"{W}x{H}")

# ---------- 2. 断点连接（小断裂自动联合） ----------
linked = link_breaks(edge, W, H, max_gap=8)
check("link increases edges", len(linked) >= len(edge),
      f"{len(edge)} -> {len(linked)}")
# 连接后闭合性：开口分量减少（闭合环端点=0）
def open_comps(es, W, H):
    unvisited = set(es)
    open_c = 0
    while unvisited:
        si = unvisited.pop()
        stack = [si]; cells = set([si])
        while stack:
            i = stack.pop()
            x, y = i % W, i // W
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    if dx==0 and dy==0: continue
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < W and 0 <= ny < H:
                        ni = ny*W+nx
                        if ni in es and ni not in cells:
                            cells.add(ni); stack.append(ni); unvisited.discard(ni)
        eps = 0
        for i in cells:
            x, y = i % W, i // W
            cnt = sum(1 for dx in (-1,0,1) for dy in (-1,0,1)
                      if not (dx==0 and dy==0) and 0 <= x+dx < W and 0 <= y+dy < H
                      and ((y+dy)*W + x+dx) in cells)
            if cnt == 1: eps += 1
        if eps > 0: open_c += 1
    return open_c
oc_before = open_comps(edge, W, H)
oc_after = open_comps(linked, W, H)
check("linking reduces open contours", oc_after < oc_before,
      f"open {oc_before} -> {oc_after}")

# ---------- 3. 闭合区域（完整轮廓→对象） ----------
regs = closed_regions(syn, p_hi=0.90)
check("closed regions >= 3", len(regs) >= 3, str([r["bbox"] for r in regs[:4]]))
def has_box(box, regs):
    for r in regs:
        b = r["bbox"]
        if abs(b[0]-box[0]) <= 7 and abs(b[1]-box[1]) <= 7                 and abs(b[2]-box[2]) <= 7 and abs(b[3]-box[3]) <= 7:
            return True
    return False
check("square region found", has_box((8, 8, 30, 30), regs),
      str([r["bbox"] for r in regs[:5]]))
check("circle region found", has_box((40, 8, 62, 30), regs),
      str([r["bbox"] for r in regs[:5]]))

# ---------- 4. 分层轮廓（整体→内部精细） ----------
hier = hierarchical_contours(syn, levels=2, p_hi=0.90)
check("hierarchical levels", len(hier) >= 3,
      str(len(hier)))
l1 = sum(len(r["children"]) for r in hier)
check("hierarchical inner contours", l1 >= 3, str(l1))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)