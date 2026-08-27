# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)
q = "运动后为什么要喝水？"
fp = st.encode(q)
print("fp:", fp)
print("运动补水 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("运动补水"))
for tr in st.DOMAIN_SYNONYM_CLUSTERS.get("运动补水", []):
    if tr in q:
        print("match:", tr)
