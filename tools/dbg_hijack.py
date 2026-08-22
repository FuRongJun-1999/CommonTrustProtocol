# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st

# 原始劫持场景：水沸腾题被大气压抢答
qs = [
    "为什么水烧开冒泡？",
    "高压锅为什么熟得快？",
    "为什么高原上水煮不熟饭？",
    "为什么海拔高的地方水烧不开？",
    "潜水为什么会有压力？",
]
for q in qs:
    fp = st.encode(q)
    print(q, "->", {k: round(v, 2) for k, v in fp.items() if k in st.REVERSE_DAILY})
