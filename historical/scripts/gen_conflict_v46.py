# -*- coding: utf-8 -*-
"""矛盾测试集 v46（燃烧/溶解/汽水气泡/血液循环·生活理化生 16 题）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么纸遇到火会烧起来？", "domain": "燃烧", "stage": "正题",
     "need": "燃烧三条件", "conflict": "燃烧 vs 灭火原理"},
    {"q": "灭火为什么要用水？", "domain": "燃烧", "stage": "正题",
     "need": "水降温隔氧", "conflict": "燃烧 vs 灭火原理"},
    {"q": "油锅着火能用水灭吗？", "domain": "燃烧", "stage": "反题",
     "need": "油比水轻更危险", "conflict": "燃烧 vs 灭火原理"},
    {"q": "怎么安全用火？", "domain": "燃烧", "stage": "合题",
     "need": "人不离火备灭火器", "conflict": "燃烧 vs 灭火原理"},
    {"q": "为什么糖放进水里会不见？", "domain": "溶解", "stage": "正题",
     "need": "溶解分散", "conflict": "溶解 vs 消失"},
    {"q": "盐放进菜里菜为什么变咸？", "domain": "溶解", "stage": "正题",
     "need": "盐溶解入味", "conflict": "溶解 vs 消失"},
    {"q": "溶解和融化一样吗？", "domain": "溶解", "stage": "反题",
     "need": "分散vs状态变", "conflict": "溶解 vs 消失"},
    {"q": "怎么让糖更快溶解？", "domain": "溶解", "stage": "合题",
     "need": "搅拌加热碾碎", "conflict": "溶解 vs 消失"},
    {"q": "为什么打开汽水会冒泡？", "domain": "汽水气泡", "stage": "正题",
     "need": "减压溶解度降低", "conflict": "气体溶解 vs 压强变化"},
    {"q": "汽水里的气泡是什么？", "domain": "汽水气泡", "stage": "正题",
     "need": "二氧化碳", "conflict": "气体溶解 vs 压强变化"},
    {"q": "为什么汽水放久了没气？", "domain": "汽水气泡", "stage": "反题",
     "need": "二氧化碳跑光", "conflict": "气体溶解 vs 压强变化"},
    {"q": "为什么摇晃汽水会喷出来？", "domain": "汽水气泡", "stage": "合题",
     "need": "气泡聚集膨胀", "conflict": "气体溶解 vs 压强变化"},
    {"q": "为什么运动后心跳会变快？", "domain": "血液循环", "stage": "正题",
     "need": "供氧需求", "conflict": "血液循环 vs 氧气需求"},
    {"q": "心脏是干什么的？", "domain": "血液循环", "stage": "正题",
     "need": "泵输送氧气养分", "conflict": "血液循环 vs 氧气需求"},
    {"q": "为什么心跳有快慢？", "domain": "血液循环", "stage": "反题",
     "need": "需求不同", "conflict": "血液循环 vs 氧气需求"},
    {"q": "怎么让心脏更健康？", "domain": "血液循环", "stage": "合题",
     "need": "运动饮食睡眠", "conflict": "血液循环 vs 氧气需求"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v46.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v46", "conflicts": 4, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v46 testset:", len(ITEMS))
