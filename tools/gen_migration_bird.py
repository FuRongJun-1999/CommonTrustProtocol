# -*- coding: utf-8 -*-
"""v49 鸟的飞行 自然问法迁移测试集归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么鸟能飞行，人不行？", "theme": "鸟的飞行"},
    {"q": "为什么鸟能飞？", "theme": "鸟的飞行"},
    {"q": "鸟是怎么飞的？", "theme": "鸟的飞行"},
    {"q": "人为什么不能像鸟一样飞？", "theme": "鸟的飞行"},
    {"q": "翅膀是怎么产生升力的？", "theme": "鸟的飞行"},
    {"q": "鸟的羽毛有什么用？", "theme": "鸟的飞行"},
    {"q": "为什么鸟的身体那么轻？", "theme": "鸟的飞行"},
    {"q": "为什么鸵鸟有翅膀却飞不起来？", "theme": "鸟的飞行"},
    {"q": "怎么让鸟飞起来？", "theme": "鸟的飞行"},
    {"q": "为什么鸟能在天上盘旋？", "theme": "鸟的飞行"},
    {"q": "小鸟翅膀一扇就飞起来，咱们人咋就那么笨重飞不起来呢？", "theme": "鸟的飞行"},
    {"q": "飞机是铁做的都能上天，咋说人连个翅膀都没有呢？", "theme": "鸟的飞行"},
    {"q": "老鹰那么能飞，是不是它的骨头特别轻才落不着地的？", "theme": "鸟的飞行"},
    {"q": "人练再多肌肉也飞不起来，是不是咱天生就缺这双翅膀？", "theme": "鸟的飞行"},
    {"q": "飞机起飞时翅膀往上扬，跟小鸟拍翅膀是不是一个道理？", "theme": "鸟的飞行"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_bird.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_bird", "themes": ["鸟的飞行"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
