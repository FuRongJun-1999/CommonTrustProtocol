# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
line = [l for l in src.splitlines() if l.startswith('    "等差数列": "')][0]
print("actual:", repr(line))
old = "通项公式：第n项等于首项加(n减1)倍公差".replace("(", "（").replace(")", "）")
print("my old:", repr(old))
print("match:", old in line)
