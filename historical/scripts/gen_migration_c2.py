# -*- coding: utf-8 -*-
"""c2 自然问法迁移测试集（8 化学概念）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "什么是化学变化？", "theme": "化学变化"},
    {"q": "铁生锈是什么变化？", "theme": "化学变化"},
    {"q": "化学变化和物理变化什么区别？", "theme": "化学变化"},
    {"q": "什么是中和反应？", "theme": "中和反应"},
    {"q": "为什么胃酸过多要吃药？", "theme": "中和反应"},
    {"q": "蚊虫叮咬怎么处理？", "theme": "中和反应"},
    {"q": "催化剂是什么？", "theme": "催化剂"},
    {"q": "催化剂会消耗吗？", "theme": "催化剂"},
    {"q": "生活里有哪些催化剂？", "theme": "催化剂"},
    {"q": "什么是元素周期律？", "theme": "元素周期律"},
    {"q": "周期表怎么排的？", "theme": "元素周期律"},
    {"q": "同一族性质相似吗？", "theme": "元素周期律"},
    {"q": "燃烧需要哪三个条件？", "theme": "燃烧条件"},
    {"q": "为什么水能灭火？", "theme": "燃烧条件"},
    {"q": "为什么有的东西点不着？", "theme": "燃烧条件"},
    {"q": "为什么撒盐雪就化了？", "theme": "盐水融雪"},
    {"q": "盐水为什么不容易结冰？", "theme": "盐水融雪"},
    {"q": "融雪剂是什么？", "theme": "盐水融雪"},
    {"q": "为什么糖是甜的盐是咸的？", "theme": "糖盐味道"},
    {"q": "糖和盐一样吗？", "theme": "糖盐味道"},
    {"q": "为什么蜂蜜放很久不会坏？", "theme": "蜂蜜防腐"},
    {"q": "蜂蜜会变质吗？", "theme": "蜂蜜防腐"},
    {"q": "蜂蜜结晶是坏了吗？", "theme": "蜂蜜防腐"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c2.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c2", "themes": ["化学变化", "中和反应", "催化剂", "元素周期律", "燃烧条件", "盐水融雪", "糖盐味道", "蜂蜜防腐"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
