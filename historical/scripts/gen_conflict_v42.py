# -*- coding: utf-8 -*-
"""矛盾测试集 v42（静电·生活物理 6 题）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么冬天脱毛衣会噼啪响？", "domain": "静电", "stage": "正题",
     "need": "摩擦起电", "conflict": "摩擦起电 vs 电流"},
    {"q": "为什么摸门把手会被电？", "domain": "静电", "stage": "正题",
     "need": "人体静电放电", "conflict": "摩擦起电 vs 电流"},
    {"q": "静电是电吗？", "domain": "静电", "stage": "反题",
     "need": "静止电荷", "conflict": "摩擦起电 vs 电流"},
    {"q": "静电有害吗？", "domain": "静电", "stage": "反题",
     "need": "一般无害", "conflict": "摩擦起电 vs 电流"},
    {"q": "怎么防静电？", "domain": "静电", "stage": "合题",
     "need": "加湿纯棉放电", "conflict": "摩擦起电 vs 电流"},
    {"q": "静电有什么用？", "domain": "静电", "stage": "合题",
     "need": "复印除尘喷涂", "conflict": "摩擦起电 vs 电流"},
]
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v42.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v42", "conflicts": 1, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("v42 testset:", len(ITEMS))
