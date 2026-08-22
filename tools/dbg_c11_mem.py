# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as st
importlib.reload(st)
print("记忆 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("记忆"))
for q in ["怎么提高记忆？", "记忆和睡眠什么关系？"]:
    fp = st.encode(q)
    print(q, "->", {k: round(v, 2) for k, v in fp.items() if k in st.REVERSE_DAILY})
