# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st

q = "为什么搓手会发热？"
fp = st.encode(q)
print("fp:", {k: round(v, 2) for k, v in fp.items() if k in st.REVERSE_DAILY})

# 模拟 _assemble 决胜
def match_len(t):
    best = len(t) if t in q else 0
    for tr in st.DOMAIN_SYNONYM_CLUSTERS.get(t, []) + st.SYNONYM_CLUSTERS.get(t, []):
        if tr in q and len(tr) > best:
            best = len(tr)
    return best
for t in ("摩擦", "发烧"):
    if t in fp and t in st.REVERSE_DAILY:
        print(t, "match_len:", match_len(t), "key_len:", len(t), "weight:", fp.get(t))
