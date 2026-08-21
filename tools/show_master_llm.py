# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_master_results.json", encoding="utf-8"))
for x in d["results"]:
    if x["route"] != "self":
        print(f"[{x['route']}] {x['q'][:50]} | {x.get('source','?')}")
        print(f"    reply: {x['reply'][:90]}")
