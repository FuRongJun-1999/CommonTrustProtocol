# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_full_results.json", encoding="utf-8"))
for x in d["results"]:
    if x["score"] < 0.5 or x["route"] in ("llm", "self_fallback"):
        print(f"[{x['route']}] score={x['score']} {x['q'][:44]} | {x.get('source','?')}")
        print(f"    reply: {x['reply'][:90]}")
