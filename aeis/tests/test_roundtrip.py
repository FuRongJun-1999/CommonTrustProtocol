# -*- coding: utf-8 -*-
"""test_roundtrip · 里程碑4.24 互逆往返误差（模板库自洽度·v0.3）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.game_web.template_lib import roundtrip_error, _lab_dist, _lab_of_rgb

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print("  PASS " + name)
    else:
        failed += 1
        print("  FAIL " + name + " " + detail)

spec = {"parts": [
    {"semantic": "legs", "color_class": "skin", "bbox": (60, 210, 100, 350)},
    {"semantic": "torso", "color_class": "blue", "bbox": (70, 95, 170, 220)},
    {"semantic": "head", "color_class": "skin", "bbox": (90, 15, 150, 90)},
    {"semantic": "hair", "color_class": "cyan", "bbox": (80, 5, 160, 50)},
]}
rt = roundtrip_error(spec)
check("roundtrip keys", set(rt) >= {"parts", "roundtrip_error",
                                    "mean_color_err", "mean_pos_err"},
      str(rt.keys()))
check("roundtrip error finite", 0 <= rt["roundtrip_error"] < 1.5,
      str(rt["roundtrip_error"]))
# torso blue 颜色往返应高度自洽（<0.05）
torso = [p for p in rt["parts"] if p["semantic"] == "torso"][0]
check("torso blue roundtrip low color err", torso["color_err"] < 0.05,
      str(torso["color_err"]))
# 颜色距离对称性
c1 = _lab_of_rgb((40, 90, 220))
c2 = _lab_of_rgb((210, 60, 50))
c3 = _lab_of_rgb((40, 90, 220))
check("lab dist zero for same", _lab_dist(c1, c3) < 1e-6)
check("lab dist red-blue > 0", _lab_dist(c1, c2) > 0.05)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
