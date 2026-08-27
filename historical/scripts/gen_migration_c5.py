# -*- coding: utf-8 -*-
"""c5 自然问法迁移测试集（6 英语语法概念）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "一般现在时怎么用？", "theme": "一般现在时"},
    {"q": "什么时候动词加s？", "theme": "一般现在时"},
    {"q": "一般现在时怎么变否定？", "theme": "一般现在时"},
    {"q": "什么是被动语态？", "theme": "被动语态"},
    {"q": "被动语态怎么构成？", "theme": "被动语态"},
    {"q": "什么时候用被动语态？", "theme": "被动语态"},
    {"q": "名词复数怎么变？", "theme": "名词复数"},
    {"q": "名词复数有什么特殊？", "theme": "名词复数"},
    {"q": "可数名词和不可数名词什么区别？", "theme": "名词复数"},
    {"q": "比较级怎么变？", "theme": "比较级"},
    {"q": "为什么有的加er有的用more？", "theme": "比较级"},
    {"q": "比较级和最高级什么区别？", "theme": "比较级"},
    {"q": "什么是定语从句？", "theme": "定语从句"},
    {"q": "关系词怎么选？", "theme": "定语从句"},
    {"q": "that和which什么区别？", "theme": "定语从句"},
    {"q": "英语时态有哪些？", "theme": "英语时态"},
    {"q": "时态表示什么？", "theme": "英语时态"},
    {"q": "现在完成时怎么用？", "theme": "英语时态"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c5.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c5", "themes": ["一般现在时", "被动语态", "名词复数", "比较级", "定语从句", "英语时态"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
