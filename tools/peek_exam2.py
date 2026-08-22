# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
for i in range(85, 95):
    print(f"line {i+1}: {lines[i][:60]}")
# 找 line 90 所属 dict
for i in range(88, 0, -1):
    s = lines[i].strip()
    if re.match(r"^[A-Z_]+\s*=\s*\{", s):
        print(f"line {i+1}: {s[:50]} <-- dict start")
        break
