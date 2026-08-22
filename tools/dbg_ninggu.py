# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
print("凝固 answer:", st.REVERSE_DAILY.get("凝固", "")[:80])
print("凝固 cluster:", st.DOMAIN_SYNONYM_CLUSTERS.get("凝固"))
import re
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
m = re.search(r'"凝固":\s*"([^"]{0,60})', src)
print("raw:", m.group(0)[:100] if m else "none")
