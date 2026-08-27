# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = {
    "光合作用": [
        "为什么天黑之后花草就不长了？",
        "家里养的花为什么放客厅就枯了？",
        "为什么摘下来的花放两天就蔫了？",
    ],
    "遗传": [
        "为什么我头发是黑的，我儿子偏偏是黄的？",
        "两个健康的爸妈怎么会生出有病的孩子？",
    ],
}
for theme, lst in qs.items():
    print(f"--- {theme} ---")
    for q in lst:
        fp = st.encode(q)
        keys = [k for k in fp if k in st.REVERSE_DAILY]
        print(f"  {q[:26]}")
        print(f"    fp={keys}")
