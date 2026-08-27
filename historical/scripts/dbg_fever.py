# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
print("发烧 cluster:", st.DOMAIN_SYNONYM_CLUSTERS.get("发烧"))
print("发烧 SYNONYM:", st.SYNONYM_CLUSTERS.get("发烧"))
# 检查发热/热 触发词分布
for w in ("发热", "热"):
    hits = {}
    for theme, lst in {**st.DOMAIN_SYNONYM_CLUSTERS, **st.SYNONYM_CLUSTERS}.items():
        for t in lst:
            if t == w or t.endswith(w):
                hits.setdefault(theme, []).append(t)
    print(f"{w} 出现于:", {k: v[:4] for k, v in hits.items()})
