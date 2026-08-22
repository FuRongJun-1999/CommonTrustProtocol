# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

def match_len(t, q):
    best = len(t) if t in q else 0
    for tr in st.DOMAIN_SYNONYM_CLUSTERS.get(t, []) + st.SYNONYM_CLUSTERS.get(t, []):
        if tr in q and len(tr) > best:
            best = len(tr)
    return best

for q in ["防晒穿什么颜色？", "散步能减肥吗？"]:
    print("===", q)
    for t in ("浅色衣服", "黑色吸热"):
        print(f"  {t}: match_len={match_len(t, q)} key_len={len(t)}")
    for t in ("散步", "身材焦虑"):
        print(f"  {t}: match_len={match_len(t, q)} key_len={len(t)}")
