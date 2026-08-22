# -*- coding: utf-8 -*-
"""c11 自然问法迁移测试集（10 簇）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么会发烧？", "theme": "发烧"},
    {"q": "发烧是坏事吗？", "theme": "发烧"},
    {"q": "发烧能捂汗吗？", "theme": "发烧"},
    {"q": "为什么会饿？", "theme": "饿"},
    {"q": "饿过头为什么反而不饿？", "theme": "饿"},
    {"q": "考试前怎么复习？", "theme": "考试"},
    {"q": "考试紧张怎么办？", "theme": "考试"},
    {"q": "考试没考好怎么办？", "theme": "考试"},
    {"q": "氧气是什么？", "theme": "氧气"},
    {"q": "人为什么要吸氧气？", "theme": "氧气"},
    {"q": "为什么叶子是绿色的？", "theme": "叶子绿色"},
    {"q": "叶绿素是什么？", "theme": "叶子绿色"},
    {"q": "为什么秋天叶子变黄？", "theme": "叶子绿色"},
    {"q": "为什么飞机比汽车快？", "theme": "飞机汽车"},
    {"q": "远途选飞机还是高铁？", "theme": "飞机汽车"},
    {"q": "什么是地球公转？", "theme": "地球公转"},
    {"q": "公转和自转什么区别？", "theme": "地球公转"},
    {"q": "为什么有闰年？", "theme": "地球公转"},
    {"q": "什么是信任？", "theme": "信任"},
    {"q": "信任怎么建立？", "theme": "信任"},
    {"q": "信任怎么破坏？", "theme": "信任"},
    {"q": "什么是价值观？", "theme": "价值观"},
    {"q": "价值观会变吗？", "theme": "价值观"},
    {"q": "价值观和道德什么区别？", "theme": "价值观"},
    {"q": "什么是记忆？", "theme": "记忆"},
    {"q": "怎么提高记忆？", "theme": "记忆"},
    {"q": "记忆和睡眠什么关系？", "theme": "记忆"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c11.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c11", "themes": ["发烧", "饿", "考试", "氧气", "叶子绿色", "飞机汽车", "地球公转", "信任", "价值观", "记忆"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
