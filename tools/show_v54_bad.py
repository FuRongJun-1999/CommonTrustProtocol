# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v54_results.json", encoding="utf-8"))
for x in d["results"]:
    if x["bad"]:
        print(f"=== [{x['domain']}] {x['q']}")
        print(f"    route={x['route']} reply={x['reply'][:130]}")
