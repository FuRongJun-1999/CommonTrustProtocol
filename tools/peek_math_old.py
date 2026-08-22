# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
for key in ("等差数列", "三角形面积", "分数定义", "奇数", "偶数"):
    m = re.search(r'    "%s": "([^"]*)"' % key, src)
    print(f"--- {key} ---")
    print(repr(m.group(1)) if m else "NONE")
