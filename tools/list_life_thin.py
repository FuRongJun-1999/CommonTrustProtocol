# -*- coding: utf-8 -*-
"""列出所有 route=? 的生活常识薄簇（SYNONYM_CLUSTERS 里的生活常识）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
cands = []
for k, v in st.REVERSE_DAILY.items():
    if len(v) < 60 and k in st.SYNONYM_CLUSTERS:
        cands.append((k, len(v)))
cands.sort(key=lambda x: x[1])
print(f"SYNONYM_CLUSTERS 薄答案(<60字): {len(cands)}")
for k, n in cands:
    print(f"  {k}: {n}ch | {st.REVERSE_DAILY[k][:30]}")
