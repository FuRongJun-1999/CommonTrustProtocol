# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)
for q in ["急刹车为什么人前冲？", "惯性是力吗？"]:
    fp = st.encode(q)
    print(q, "->", fp)
print("惯性 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("惯性"))
