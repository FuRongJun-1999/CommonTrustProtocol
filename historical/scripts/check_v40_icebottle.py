# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
for v in ("v40", "v37"):
    p = r"D:\Program Files\2_ai\knowledge-base\conflict_testset_%s.json" % v
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print(v, "ERR", e); continue
    items = d.get("items", [])
    ice_bottle = [x["q"] for x in items if "可乐" in x["q"] or "水珠" in x["q"] or "瓶" in x["q"]]
    print(f"--- {v} ({len(items)} items) 瓶外水珠相关 ---")
    for q in ice_bottle:
        print("  ", q)
