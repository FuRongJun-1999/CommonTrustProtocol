# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = [
    "为什么水到100°C就开？",
    "为什么烧水会有声音？",
    "为什么水会冻成冰？",
    "怎么让水不结冰？",
    "为什么冰块在常温下会化成水？",
    "熔化和融化一样吗？",
    "怎么让冰化得快？",
    "冰水混合为什么还是0°C？",
    "雪是怎么形成的？",
]
for q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    print(f"{q[:20]}")
    print(f"   fp={keys}")
