# -*- coding: utf-8 -*-
"""扫描剩余 <120 字的簇（所有域）——找还值得升级的常识候选"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
thin = []
for k, v in st.REVERSE_DAILY.items():
    if len(v) < 120 and k in st.DOMAIN_SYNONYM_CLUSTERS:
        route = st.DOMAIN_ROUTE.get(k, "?")
        thin.append((k, len(v), route))
thin.sort(key=lambda x: x[1])
print(f"剩余 <120字 簇: {len(thin)}")
for k, n, route in thin[:40]:
    print(f"  {k}: {n}ch route={route}")
