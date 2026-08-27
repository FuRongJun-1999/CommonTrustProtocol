# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
for i in range(113, 200):
    s = lines[i].strip()
    if s == "}":
        print(f"line {i+1}: }}  <- dict end")
        print(f"  prev: {lines[i-1][:60]}")
        print(f"  next: {lines[i+1][:60]}")
        break
    if s == "}" or s.startswith("}"):
        print(f"line {i+1}: {s[:30]}")
