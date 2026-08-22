# -*- coding: utf-8 -*-
"""round15 LLM 变异 vs 清理后簇——真实迁移率"""
import sys, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st
importlib.reload(st)

qs = {
    "降落伞": [
        "为什么从楼顶不小心掉下来的东西落得很慢？",
        "为什么用布条可以让人慢一点降落？",
        "为什么小鸟从很高掉下来没事？",
    ],
    "秋千": [
        "为什么公园秋千一推就能荡很久？",
        "为什么荡秋千时身体前后晃？",
        "为什么小朋友荡秋千使劲蹬腿就越来越高？",
    ],
    "反射": [
        "为什么镜子里的我左手却朝右，头脚却不变？",
        "对着镜子挥手，手伸不进去，为什么能看到手却摸不到？",
        "站在河边，为什么水里的倒影是头朝下脚朝上？",
        "为什么汽车后视镜里的车看起来比实际远？",
        "为什么游乐场的哈哈镜能把人照变形？",
        "为什么湖面倒影总是有点模糊，不像镜子那么清楚？",
    ],
    "蒸发": [
        "为什么出完汗没擦掉，一会儿身上就干了？",
        "小区泳池的水天天换，到底跑到哪儿去了？",
        "太阳一晒，地里的积水咋就没了？",
        "衣服晾在外面怎么越晒越干，水去哪儿了？",
    ],
}
total_ok = total = 0
for theme, lst in qs.items():
    ok = sum(1 for q in lst if theme in st.encode(q))
    total_ok += ok; total += len(lst)
    print(f"{theme}: {ok}/{len(lst)}")
print(f"--- total {total_ok}/{total} ---")
