# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
print("沸点与气压 answer:", st.REVERSE_DAILY.get("沸点与气压", "")[:120])
print()
q = "为什么高原上水煮不熟饭？"
fp = st.encode(q)
print("fp all:", {k: round(v, 2) for k, v in fp.items()})
# 模拟 _assemble 的决胜
def match_len(t):
    best = len(t) if t in q else 0
    for tr in st.DOMAIN_SYNONYM_CLUSTERS.get(t, []) + st.SYNONYM_CLUSTERS.get(t, []):
        if tr in q and len(tr) > best:
            best = len(tr)
    return best
for t in ("沸腾", "沸点与气压", "煮鸡蛋"):
    print(t, "match_len:", match_len(t), "len:", len(t), "weight:", fp.get(t))
