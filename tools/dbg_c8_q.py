# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)
for q in ["防晒穿什么颜色？", "饭后散步好不好？", "散步能减肥吗？"]:
    fp = st.encode(q)
    print(q, "->", {k: round(v, 2) for k, v in fp.items() if k in st.REVERSE_DAILY})
# 检查 CHITCHAT
from wisdom.chat_engine import CHITCHAT
for q in ["饭后散步好不好？", "每天散步好吗？"]:
    for words, reply in CHITCHAT:
        for w in words:
            if w in q:
                print(f"chitchat hit: {q} -> {w!r}")
