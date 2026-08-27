# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = [
    "为什么蜡烛能一直烧？",
    "冰块掉进水里，到底是化了还是溶进去了？",
    "为什么泡枸杞要用热水？",
    "老年人手脚总是冰凉，是不是身体有问题？",
    "压力大时总觉得胸闷气短，心脏是不是累了？",
    "久坐不动的人更容易犯困，为什么？",
    "经常加班熬夜的人，心脏能扛得住吗？",
    "运动员心跳慢，是不是比普通人更健康？",
]
for q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    print(f"{q[:26]}")
    print(f"   fp={keys}")
