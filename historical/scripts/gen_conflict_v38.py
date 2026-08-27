# -*- coding: utf-8 -*-
"""矛盾测试集 v38（自然现象·彩虹 6 题）"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

ITEMS = [
    {"q": "为什么雨后有时会有彩虹？", "domain": "彩虹", "stage": "正题",
     "need": "条件凑齐", "conflict": "光的折射 vs 观测条件"},
    {"q": "彩虹是怎么形成的？", "domain": "彩虹", "stage": "正题",
     "need": "折射色散", "conflict": "光的折射 vs 观测条件"},
    {"q": "为什么有时候雨后没有彩虹？", "domain": "彩虹", "stage": "反题",
     "need": "条件缺了", "conflict": "光的折射 vs 观测条件"},
    {"q": "彩虹是实体吗？", "domain": "彩虹", "stage": "反题",
     "need": "光学的像", "conflict": "光的折射 vs 观测条件"},
    {"q": "什么时候最容易看到彩虹？", "domain": "彩虹", "stage": "合题",
     "need": "时机位置", "conflict": "光的折射 vs 观测条件"},
    {"q": "为什么彩虹是弯的？", "domain": "彩虹", "stage": "合题",
     "need": "42度角", "conflict": "光的折射 vs 观测条件"},
]

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v38.json", "w", encoding="utf-8") as f:
    json.dump({"name": "conflict_testset_v38", "conflicts": 1, "items": ITEMS},
              f, ensure_ascii=False, indent=1)
print("v38 testset:", len(ITEMS), "items")
