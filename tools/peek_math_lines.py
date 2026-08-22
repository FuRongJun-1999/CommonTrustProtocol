# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
for key in ("等差数列", "加法"):
    for i, line in enumerate(src.splitlines(), 1):
        if ('"%s"' % key) in line:
            print(f"line {i}: {repr(line[:40])}")
