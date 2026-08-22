# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
# 找含 飞/鸟/翅/翼 的触发词分布在哪些簇
for w in ("飞", "鸟", "翅", "翼", "机"):
    hits = {}
    for theme, lst in st.DOMAIN_SYNONYM_CLUSTERS.items():
        for t in lst:
            if w in t:
                hits.setdefault(theme, []).append(t)
    print(f"=== {w} 出现于 {len(hits)} 个簇 ===")
    for theme, lst in list(hits.items())[:12]:
        print(f"   {theme}: {lst[:6]}")
