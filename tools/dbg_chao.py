# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
print("潮汐 ans:", repr(st.REVERSE_DAILY.get("潮汐", ""))[:80])
print("潮汐 cluster:", st.DOMAIN_SYNONYM_CLUSTERS.get("潮汐"))
# 检查潮汐升级答案是否写入了
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
import re
m = re.search(r'"潮汐":\s*"([^"]{0,50})', src)
print("raw:", m.group(1)[:50] if m else "none")
