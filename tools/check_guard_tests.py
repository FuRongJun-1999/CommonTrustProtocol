# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
for v in ("v37", "v40", "v41", "v42", "v43", "v44", "v45", "v46", "v47"):
    p = r"D:\Program Files\2_ai\knowledge-base\conflict_testset_%s.json" % v
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    for x in d.get("items", []):
        q = x["q"]
        if any(w in q for w in ("珠峰", "珠穆朗玛", "高原", "山顶", "高压锅", "海拔", "气压", "潜水", "深海")):
            print(f"{v} | {q}")
