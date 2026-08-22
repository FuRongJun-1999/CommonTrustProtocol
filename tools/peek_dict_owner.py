# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
# 找 line 1150 所属 dict——向上找最近的行首 = { 或缩进0的 { 结尾
for i in range(1149, 900, -1):
    s = lines[i].strip()
    if s.endswith("= {") or s == "= {":
        print(f"line {i+1}: {lines[i][:60]}")
        break
# 也检查 line 135 到 1150 之间是否插入了别的 dict 定义
import re
for i in range(113, 1150):
    if re.match(r"^[A-Z_]+\s*=\s*\{", lines[i]):
        print(f"dict def at line {i+1}: {lines[i][:50]}")
