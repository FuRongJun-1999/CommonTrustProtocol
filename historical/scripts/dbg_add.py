# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
key = "加法"
old = "1加1等于2——这是最基础的算术"
pat = r'    "%s": "' % key
print("pat:", repr(pat))
found = False
for m in re.finditer(pat, src):
    ls = m.start(); le = src.index("\n", ls)
    line = src[ls:le]
    print("match:", repr(line[:70]), "| old in:", old in line)
    if old in line:
        found = True
        break
print("found:", found)
