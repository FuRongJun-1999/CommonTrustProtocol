# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
# 从 line 114 开始找行首为 } 的行
for i in range(113, 160):
    if lines[i].strip() == "}":
        print(f"DOMAIN dict ends at line {i+1}: {lines[i]}")
        # 之后的行
        print(f"  next: {lines[i+1][:50] if i+1 < len(lines) else 'EOF'}")
        break
