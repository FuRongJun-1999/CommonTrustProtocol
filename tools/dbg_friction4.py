# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

q = "为什么搓手会发热？"
cl = st.DOMAIN_SYNONYM_CLUSTERS.get("摩擦", [])
for tr in cl:
    print(repr(tr), "in q:", tr in q, "len:", len(tr))
print()
print("q repr:", repr(q))
