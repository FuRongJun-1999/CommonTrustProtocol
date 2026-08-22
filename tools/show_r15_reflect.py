# -*- coding: utf-8 -*-
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = [
    "为什么镜子里的我左手却朝右，头脚却不变？",
    "对着镜子挥手，手伸不进去，为什么能看到手却摸不到？",
    "站在河边，为什么水里的倒影是头朝下脚朝上？",
    "为什么汽车后视镜里的车看起来比实际远？",
    "为什么游乐场的哈哈镜能把人照变形？",
    "为什么湖面倒影总是有点模糊，不像镜子那么清楚？",
]
for q in qs:
    fp = st.encode(q)
    hit = "反射" in fp
    print(f"{'HIT' if hit else 'MISS'} {q[:26]} | fp={[k for k in fp if k in st.REVERSE_DAILY]}")
