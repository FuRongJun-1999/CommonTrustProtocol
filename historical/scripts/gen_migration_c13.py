# -*- coding: utf-8 -*-
"""c13 自然问法迁移测试集（12 簇）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "一年有多少个月？", "theme": "一年月数"},
    {"q": "为什么一年有12个月？", "theme": "一年月数"},
    {"q": "2月为什么只有28天？", "theme": "一年月数"},
    {"q": "一周有几天？", "theme": "一周天数"},
    {"q": "星期是怎么来的？", "theme": "一周天数"},
    {"q": "一天有多少个小时？", "theme": "一天小时"},
    {"q": "一小时为什么是60分钟？", "theme": "一天小时"},
    {"q": "为什么天空是蓝色的？", "theme": "天空蓝色"},
    {"q": "为什么傍晚天空变红？", "theme": "天空蓝色"},
    {"q": "月亮为什么会发光？", "theme": "月亮发光"},
    {"q": "为什么月亮形状会变？", "theme": "月亮发光"},
    {"q": "为什么船能浮在水上？", "theme": "船浮水上"},
    {"q": "铁做的船为什么不沉？", "theme": "船浮水上"},
    {"q": "什么是应力？", "theme": "应力"},
    {"q": "应力大了会怎样？", "theme": "应力"},
    {"q": "什么是短路？", "theme": "短路"},
    {"q": "短路为什么会起火？", "theme": "短路"},
    {"q": "为什么混凝土要加钢筋？", "theme": "混凝土钢筋"},
    {"q": "钢筋在混凝土里干什么？", "theme": "混凝土钢筋"},
    {"q": "什么是细胞？", "theme": "细胞"},
    {"q": "细胞怎么变多？", "theme": "细胞"},
    {"q": "什么是原子？", "theme": "原子"},
    {"q": "原子里面有什么？", "theme": "原子"},
    {"q": "为什么声音需要介质？", "theme": "介质"},
    {"q": "真空里能听到声音吗？", "theme": "介质"},
]
themes = ["一年月数", "一周天数", "一天小时", "天空蓝色", "月亮发光", "船浮水上",
          "应力", "短路", "混凝土钢筋", "细胞", "原子", "介质"]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c13.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c13", "themes": themes, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS), "题,", len(themes), "主题")
