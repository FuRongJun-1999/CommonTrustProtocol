# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
print("沸点与气压 cluster:", st.DOMAIN_SYNONYM_CLUSTERS.get("沸点与气压"))
print("沸点与气压 in REVERSE:", "沸点与气压" in st.REVERSE_DAILY)
q = "为什么高原上水煮不熟饭？"
fp = st.encode(q)
print("fp:", {k: v for k, v in fp.items() if k in st.REVERSE_DAILY})
print("沸腾 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("沸腾"))
