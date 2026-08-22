# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v46_results.json", encoding="utf-8"))
for x in d["results"]:
    if x["bad"]:
        print(x["q"], "| route:", x["route"])
        print("  reply:", x["reply"][:160])
