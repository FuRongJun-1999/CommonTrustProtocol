# -*- coding: utf-8 -*-
"""identify 审计（常识域）：全部簇中【常识类】主题的答案长度普查
常识类 = 生活常识/学科基础/社会常识（排除前端/深度专业概念）
输出：薄答案(<60字) 清单 + 缺失直答清单
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st

# 常识域路由（生活/学科基础）
COMMON_ROUTES = {"物理学", "化学", "生物学", "天文学", "地理学", "小学科学",
                 "数学", "英语", "语文", "编程语言", "经济学", "政治", "计算机科学"}
# 深度专业路由（非常识，跳过）
DEEP_ROUTES = {"工程学", "负反馈系统", "智能论", "价值理论与AI对齐", "自我意识"}

print("=== 常识域薄答案审计（<60字） ===")
thin = []
for k in st.DOMAIN_SYNONYM_CLUSTERS:
    route = st.DOMAIN_ROUTE.get(k, "")
    if route not in COMMON_ROUTES or route in DEEP_ROUTES:
        continue
    ans = st.REVERSE_DAILY.get(k, "")
    n = len(ans)
    if n < 60:
        thin.append((k, n, route, st.DOMAIN_SYNONYM_CLUSTERS[k][:4]))
for k, n, route, cl in sorted(thin, key=lambda x: x[1]):
    print(f"  {k}: ans={n}ch route={route} cluster={cl}")

print(f"\n薄答案常识簇数: {len(thin)}")

# 缺失直答（簇存在但 REVERSE_DAILY 无键）
print("\n=== 缺失直答（有簇无直答） ===")
missing = [k for k in st.DOMAIN_SYNONYM_CLUSTERS
           if st.DOMAIN_ROUTE.get(k, "") in COMMON_ROUTES
           and k not in st.REVERSE_DAILY]
print(f"  缺失数: {len(missing)}")
for k in missing[:40]:
    print(f"  {k}: {st.DOMAIN_SYNONYM_CLUSTERS[k][:4]}")
