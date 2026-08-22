# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
for c in ("感冒", "流感", "发烧", "咳嗽", "疫苗犹豫", "免疫"):
    cl = st.DOMAIN_SYNONYM_CLUSTERS.get(c, [])
    rev = len(st.REVERSE_DAILY.get(c, ""))
    print(f"{c}: cluster={len(cl)} [{cl[:8]}] ans={rev}ch")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
hits = re.findall(r'"([^"]*感冒[^"]*)"', src)
print("感冒 in clusters:", set(hits))
hits2 = re.findall(r'"([^"]*发烧[^"]*)"', src)
print("发烧 in clusters:", set(hits2))
