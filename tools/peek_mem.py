# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
lines = src.splitlines()
for i, line in enumerate(lines):
    if '"记忆"' in line and '[' in line:
        print(f"line {i+1}: {line[:90]}")
# 检查记忆是否在 DOMAIN 和 SYNONYM
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as st
print("DOMAIN 记忆:", st.DOMAIN_SYNONYM_CLUSTERS.get("记忆"))
print("SYNONYM 记忆:", st.SYNONYM_CLUSTERS.get("记忆"))
