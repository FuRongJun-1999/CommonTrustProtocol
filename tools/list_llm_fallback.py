# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_full_results.json", encoding="utf-8"))
print("llm 兜底题（可加固为 self 直答）:")
for x in d["results"]:
    if x["route"] == "llm":
        print(f"  [{x.get('source','?')}] {x['q'][:46]} | keys={x.get('keys')}")
print(f"\n共 {sum(1 for x in d['results'] if x['route']=='llm')} 题 llm")
