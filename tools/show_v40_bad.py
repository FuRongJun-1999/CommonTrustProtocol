# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v40_results.json", encoding="utf-8"))
print("v40:", d["total"], d["ok"])
for x in d["results"]:
    if x["bad"]:
        print(f"BAD [{x['domain']}/{x['stage']}] {x['q']}")
        print("  route:", x["route"], "| reply:", x["reply"][:120])
