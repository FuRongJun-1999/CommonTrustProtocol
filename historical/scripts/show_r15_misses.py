# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = [
    "为什么从楼顶不小心掉下来的东西落得很慢？",
    "为什么用布条可以让人慢一点降落？",
    "为什么小鸟从很高掉下来没事？",
    "为什么湖面倒影总是有点模糊，不像镜子那么清楚？",
    "为什么出完汗没擦掉，一会儿身上就干了？",
    "小区泳池的水天天换，到底跑到哪儿去了？",
]
for q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    print(f"{q[:26]}")
    print(f"   fp={keys}")
