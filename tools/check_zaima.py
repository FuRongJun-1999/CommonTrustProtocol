# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
for v in range(37, 52):
    p = r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v%d.json" % v
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    for x in d.get("items", []):
        if "在吗" in x["q"]:
            print(f"v{v}: {x['q']}")
print("done")
