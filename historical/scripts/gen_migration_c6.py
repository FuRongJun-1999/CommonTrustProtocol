# -*- coding: utf-8 -*-
"""c6 自然问法迁移测试集（7 经济/计算机概念）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么供大于求会降价？", "theme": "供需求"},
    {"q": "为什么供不应求会涨价？", "theme": "供需求"},
    {"q": "价格是怎么定的？", "theme": "供需求"},
    {"q": "通货膨胀是什么？", "theme": "通货膨胀"},
    {"q": "为什么钱越来越不值钱？", "theme": "通货膨胀"},
    {"q": "怎么应对通货膨胀？", "theme": "通货膨胀"},
    {"q": "什么是机会成本？", "theme": "机会成本"},
    {"q": "机会成本怎么算？", "theme": "机会成本"},
    {"q": "机会成本和沉没成本什么区别？", "theme": "机会成本"},
    {"q": "二进制是什么？", "theme": "二进制"},
    {"q": "为什么计算机用二进制？", "theme": "二进制"},
    {"q": "一个字节是什么？", "theme": "二进制"},
    {"q": "数据库是什么？", "theme": "数据库"},
    {"q": "怎么查数据库的数据？", "theme": "数据库"},
    {"q": "数据库和Excel什么区别？", "theme": "数据库"},
    {"q": "什么是递归？", "theme": "递归"},
    {"q": "递归为什么要终止条件？", "theme": "递归"},
    {"q": "递归和循环什么区别？", "theme": "递归"},
    {"q": "什么是面向对象？", "theme": "面向对象"},
    {"q": "类和对象什么关系？", "theme": "面向对象"},
    {"q": "面向对象和面向过程什么区别？", "theme": "面向对象"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c6.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c6", "themes": ["供需求", "通货膨胀", "机会成本", "二进制", "数据库", "递归", "面向对象"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
