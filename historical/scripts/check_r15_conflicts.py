# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
for c in ("浮力", "重力", "惯性", "杠杆", "滑轮", "自由落体"):
    print(c, "->", st.DOMAIN_SYNONYM_CLUSTERS.get(c))
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
for w in ("降落伞", "秋千", "摆", "荡"):
    hits = re.findall(r'"([^"]*' + w + r'[^"]*)"', src)
    print(w, "in clusters:", set(hits[:10]))
