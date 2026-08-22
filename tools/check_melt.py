# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()
for theme in ("熔化", "结冰"):
    m = re.search(r'"%s":\s*\[([^\]]*)\]' % theme, src)
    print(f"--- {theme} ---")
    print(m.group(1) if m else "(none)")
# 检查融化/融雪 触发词分布
import wisdom.semantic_translate as st
for t in ("融化", "融雪", "化掉", "化开"):
    hits = [k for k, v in {**st.DOMAIN_SYNONYM_CLUSTERS, **st.SYNONYM_CLUSTERS}.items() if any(t in x for x in v)]
    print(t, "->", hits)
