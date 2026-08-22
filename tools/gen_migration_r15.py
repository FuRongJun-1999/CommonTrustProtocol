# -*- coding: utf-8 -*-
"""round15 自然问法迁移测试集（降落伞/秋千/反射/蒸发）——固定归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么从楼顶不小心掉下来的东西落得很慢？", "theme": "降落伞"},
    {"q": "为什么用布条可以让人慢一点降落？", "theme": "降落伞"},
    {"q": "为什么小鸟从很高掉下来没事？", "theme": "降落伞"},
    {"q": "为什么公园秋千一推就能荡很久？", "theme": "秋千"},
    {"q": "为什么荡秋千时身体前后晃？", "theme": "秋千"},
    {"q": "为什么小朋友荡秋千使劲蹬腿就越来越高？", "theme": "秋千"},
    {"q": "为什么镜子里的我左手却朝右，头脚却不变？", "theme": "反射"},
    {"q": "对着镜子挥手，手伸不进去，为什么能看到手却摸不到？", "theme": "反射"},
    {"q": "站在河边，为什么水里的倒影是头朝下脚朝上？", "theme": "反射"},
    {"q": "为什么汽车后视镜里的车看起来比实际远？", "theme": "反射"},
    {"q": "为什么游乐场的哈哈镜能把人照变形？", "theme": "反射"},
    {"q": "为什么湖面倒影总是有点模糊，不像镜子那么清楚？", "theme": "反射"},
    {"q": "为什么出完汗没擦掉，一会儿身上就干了？", "theme": "蒸发"},
    {"q": "小区泳池的水天天换，到底跑到哪儿去了？", "theme": "蒸发"},
    {"q": "太阳一晒，地里的积水咋就没了？", "theme": "蒸发"},
    {"q": "衣服晾在外面怎么越晒越干，水去哪儿了？", "theme": "蒸发"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_r15.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_r15", "themes": ["降落伞", "秋千", "反射", "蒸发"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
