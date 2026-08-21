# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_full_results.json", encoding="utf-8"))
targets = ["科学方法论", "智能论", "二阶常系数线性方程", "核与像", "相似对角化",
           "极限运算法则", "方向导数与梯度", "回溯与分支限界"]
for x in d["results"]:
    for t in targets:
        if t in x["q"]:
            print(f"[{x['source']}] {x['q']}")
            print(f"  route={x['route']} reply: {x['reply'][:110]}")
            print()
            break
