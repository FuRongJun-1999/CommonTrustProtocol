# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)
for q in ["为什么饭后不能马上运动？", "类和对象什么区别？"]:
    fp = st.encode(q)
    print(q, "->", {k: round(v, 2) for k, v in fp.items()})
print("饭后运动 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("饭后运动"))
print("编程类 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("编程类"))
print("面向对象 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("面向对象"))
