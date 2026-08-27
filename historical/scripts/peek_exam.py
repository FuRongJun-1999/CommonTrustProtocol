# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
for i, line in enumerate(lines):
    if '"考试"' in line and '[' in line:
        print(f"line {i+1}: {line[:80]}")
