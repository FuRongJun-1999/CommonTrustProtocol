# -*- coding: utf-8 -*-
"""矛盾测试集 v48（沸腾/液化/凝固/熔化/升华/凝华·物态变化六簇 16 题）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么水烧开会咕嘟咕嘟冒泡？", "domain": "沸腾", "stage": "正题",
     "need": "内部汽化", "conflict": "沸腾 vs 蒸发"},
    {"q": "为什么高原上水煮不熟饭？", "domain": "沸腾", "stage": "反题",
     "need": "气压低沸点低", "conflict": "沸腾 vs 蒸发"},
    {"q": "怎么判断水烧开了？", "domain": "沸腾", "stage": "合题",
     "need": "翻滚+白气+100°C", "conflict": "沸腾 vs 蒸发"},
    {"q": "为什么哈气在镜子上会变成小水珠？", "domain": "液化", "stage": "正题",
     "need": "遇冷液化", "conflict": "液化 vs 凝结"},
    {"q": "冬天眼镜进屋为什么起雾？", "domain": "液化", "stage": "正题",
     "need": "冷镜片遇热水汽", "conflict": "液化 vs 凝结"},
    {"q": "露水是从天上掉下来的吗？", "domain": "液化", "stage": "反题",
     "need": "夜里水蒸气液化", "conflict": "液化 vs 凝结"},
    {"q": "凝固是熔化的逆过程吗？", "domain": "凝固", "stage": "反题",
     "need": "液体→固体放热", "conflict": "凝固 vs 熔化"},
    {"q": "怎么让水不结冰？", "domain": "凝固", "stage": "合题",
     "need": "保温+加盐+流动", "conflict": "凝固 vs 熔化"},
    {"q": "为什么冰块在常温下会化成水？", "domain": "熔化", "stage": "正题",
     "need": "吸热熔化", "conflict": "熔化 vs 融化"},
    {"q": "熔化和融化一样吗？", "domain": "熔化", "stage": "反题",
     "need": "固体变液体", "conflict": "熔化 vs 融化"},
    {"q": "怎么让冰化得快？", "domain": "熔化", "stage": "合题",
     "need": "高温+敲碎+盐", "conflict": "熔化 vs 融化"},
    {"q": "为什么樟脑丸放衣柜里会变小？", "domain": "升华", "stage": "正题",
     "need": "固体直接变气体", "conflict": "升华 vs 蒸发"},
    {"q": "升华是吸热还是放热？", "domain": "升华", "stage": "反题",
     "need": "吸热", "conflict": "升华 vs 凝华"},
    {"q": "为什么冬天窗户上会有霜花？", "domain": "凝华", "stage": "正题",
     "need": "水蒸气直接变冰晶", "conflict": "凝华 vs 液化"},
    {"q": "雪是水滴冻成的吗？", "domain": "凝华", "stage": "反题",
     "need": "云里水蒸气凝华", "conflict": "凝华 vs 液化"},
    {"q": "凝华和液化有什么区别？", "domain": "凝华", "stage": "反题",
     "need": "变冰晶vs变水珠", "conflict": "凝华 vs 液化"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v48.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v48", "conflicts": 6, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v48 testset:", len(ITEMS))
