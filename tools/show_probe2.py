# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\rebuild_probe2_results.json", encoding="utf-8"))
print(f"共 {len(d)} 题")
llm = [x for x in d if x["route"] == "llm"]
print(f"llm 兜底: {len(llm)}")
for x in llm:
    print(f"  [{x['card']}] {x['q']} | {x['reply'][:50]}")
print("\nself:", len(d) - len(llm))
