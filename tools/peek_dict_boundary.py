# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
# 找 line 114 后第一个行首为 } 的行（dict 结束）
depth = 0
for i in range(113, 300):
    line = lines[i]
    if line.rstrip().endswith("{"):
        pass
    if line.strip() == "}" or line.strip().startswith("}"):
        print(f"dict ends at line {i+1}: {line.strip()[:20]}")
        break
# 打印 line 135 上下文确认所属 dict
for i in range(125, 140):
    print(f"line {i+1}: {lines[i][:50]}")
