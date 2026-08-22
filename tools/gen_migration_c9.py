# -*- coding: utf-8 -*-
"""c9 自然问法迁移测试集（12 剩余常识）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "杠杆原理是什么？", "theme": "杠杆原理"},
    {"q": "生活里有哪些杠杆？", "theme": "杠杆原理"},
    {"q": "电流方向怎么判断？", "theme": "电流方向"},
    {"q": "交流电和直流电什么区别？", "theme": "电流方向"},
    {"q": "为什么西瓜比苹果大？", "theme": "苹果西瓜"},
    {"q": "西瓜和苹果哪个解暑？", "theme": "苹果西瓜"},
    {"q": "什么是惯性？", "theme": "惯性"},
    {"q": "急刹车为什么人前冲？", "theme": "惯性"},
    {"q": "惯性是力吗？", "theme": "惯性"},
    {"q": "什么是修辞手法？", "theme": "修辞手法"},
    {"q": "比喻和拟人什么区别？", "theme": "修辞手法"},
    {"q": "分子热运动是什么？", "theme": "分子热运动"},
    {"q": "为什么热水能洗掉油污？", "theme": "分子热运动"},
    {"q": "为什么油浮在水上？", "theme": "水油密度"},
    {"q": "水和油为什么不溶？", "theme": "水油密度"},
    {"q": "什么是自由落体？", "theme": "自由落体"},
    {"q": "铁球和羽毛为什么同时落地？", "theme": "自由落体"},
    {"q": "声音是怎么传播的？", "theme": "声音传播"},
    {"q": "声音能在真空中传播吗？", "theme": "声音传播"},
    {"q": "Rust 是什么？", "theme": "Rust"},
    {"q": "Rust 为什么内存安全？", "theme": "Rust"},
    {"q": "TypeScript 是什么？", "theme": "TypeScript"},
    {"q": "TS 和 JS 什么区别？", "theme": "TypeScript"},
    {"q": "Python 是什么？", "theme": "Python"},
    {"q": "Python 为什么慢？", "theme": "Python"},
    {"q": "GIL 是什么？", "theme": "Python"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c9.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c9", "themes": ["杠杆原理", "电流方向", "苹果西瓜", "惯性", "修辞手法", "分子热运动", "水油密度", "自由落体", "声音传播", "Rust", "TypeScript", "Python"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
