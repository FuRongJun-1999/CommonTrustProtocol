# -*- coding: utf-8 -*-
"""矛盾测试集 v45（感冒/光合作用/遗传/萌发·生活生物 16 题）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么天冷容易感冒？", "domain": "感冒", "stage": "正题",
     "need": "病毒入侵", "conflict": "病毒入侵 vs 免疫力"},
    {"q": "感冒不吃药能好吗？", "domain": "感冒", "stage": "正题",
     "need": "病毒自愈", "conflict": "病毒入侵 vs 免疫力"},
    {"q": "感冒是冻出来的吗？", "domain": "感冒", "stage": "反题",
     "need": "受凉是帮凶", "conflict": "病毒入侵 vs 免疫力"},
    {"q": "感冒和流感一样吗？", "domain": "感冒", "stage": "反题",
     "need": "流感症状重", "conflict": "病毒入侵 vs 免疫力"},
    {"q": "怎么预防感冒？", "domain": "感冒", "stage": "合题",
     "need": "洗手通风锻炼睡眠", "conflict": "病毒入侵 vs 免疫力"},
    {"q": "为什么叶子是绿的？", "domain": "光合作用", "stage": "正题",
     "need": "叶绿素反射绿光", "conflict": "光合作用 vs 能量来源"},
    {"q": "植物为什么要晒太阳？", "domain": "光合作用", "stage": "正题",
     "need": "光合作用制造养分", "conflict": "光合作用 vs 能量来源"},
    {"q": "植物晚上也进行光合作用吗？", "domain": "光合作用", "stage": "反题",
     "need": "晚上只呼吸", "conflict": "光合作用 vs 能量来源"},
    {"q": "怎么让植物长得好？", "domain": "光合作用", "stage": "合题",
     "need": "光照水肥", "conflict": "光合作用 vs 能量来源"},
    {"q": "为什么孩子长得像父母？", "domain": "遗传", "stage": "正题",
     "need": "基因各一半", "conflict": "遗传 vs 变异"},
    {"q": "兄弟姐妹为什么长得不一样？", "domain": "遗传", "stage": "反题",
     "need": "基因重新组合", "conflict": "遗传 vs 变异"},
    {"q": "遗传决定一切吗？", "domain": "遗传", "stage": "合题",
     "need": "遗传倾向环境表现", "conflict": "遗传 vs 变异"},
    {"q": "为什么种子浇水就会发芽？", "domain": "萌发", "stage": "正题",
     "need": "水唤醒种子", "conflict": "生命启动 vs 条件满足"},
    {"q": "种子发芽需要什么条件？", "domain": "萌发", "stage": "正题",
     "need": "水空气温度", "conflict": "生命启动 vs 条件满足"},
    {"q": "种子发芽需要光吗？", "domain": "萌发", "stage": "反题",
     "need": "多数不需要光", "conflict": "生命启动 vs 条件满足"},
    {"q": "怎么种种子更容易发芽？", "domain": "萌发", "stage": "合题",
     "need": "浸种湿润适温", "conflict": "生命启动 vs 条件满足"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v45.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v45", "conflicts": 4, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v45 testset:", len(ITEMS))
