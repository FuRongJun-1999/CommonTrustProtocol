# -*- coding: utf-8 -*-
"""identify 审计（final）：物理学/化学/生物学 路由下所有簇——找答案缺失或过薄的簇
（<60字 = 一句话直答，生活主题应升级；缺失 = 需补直答）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st

LIFE_ROUTES = ("物理学", "化学", "生物学", "天文学", "地理学")
print("=== identify 审计：生活域簇 → 答案长度 ===")
thin = []
for k in st.DOMAIN_SYNONYM_CLUSTERS:
    route = st.DOMAIN_ROUTE.get(k, "")
    if route not in LIFE_ROUTES:
        continue
    ans = st.REVERSE_DAILY.get(k, "")
    n = len(ans)
    if n < 60:
        thin.append((k, n, route, st.DOMAIN_SYNONYM_CLUSTERS[k][:6]))
for k, n, route, cl in sorted(thin, key=lambda x: x[1]):
    print(f"  {k}: ans={n}ch route={route} cluster={cl}")
print(f"\n薄/缺答案簇数: {len(thin)}")
