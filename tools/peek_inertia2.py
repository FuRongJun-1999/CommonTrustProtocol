# -*- coding: utf-8 -*-
import sys, importlib, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)
print("DOMAIN 惯性:", st.DOMAIN_SYNONYM_CLUSTERS.get("惯性"))
print("SYNONYM 惯性:", st.SYNONYM_CLUSTERS.get("惯性"))
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
for i, line in enumerate(src.splitlines(), 1):
    if '"惯性"' in line and '[' in line:
        print(f"line {i}: {line[:60]}")
