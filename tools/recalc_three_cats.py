# -*- coding: utf-8 -*-
"""用修正后的 keys 重算三类成绩（不重跑，用 three_cats_results_v17.json + 新 dialogue_1000 keys）"""
import json, sys, re
sys.stdout.reconfigure(encoding="utf-8")
HERE = r"D:\Program Files\2_ai\knowledge-base"

# 载入修正后的 dialogue_1000（含新 keys）
data = json.load(open(HERE + r"\dialogue_1000.json", encoding="utf-8"))
q2keys = {}
for item in data:
    q2keys[item["q"]] = item["keys"]

# 三类测试结果（v1.17 代码跑的回复）
results = json.load(open(HERE + r"\three_cats_results_v17.json", encoding="utf-8"))

def norm(s):
    return re.sub(r"[\s^]", "", s or "").replace("²","2").replace("³","3")

def score_keys(reply, keys):
    rn = norm(reply)
    return 1.0 if any(norm(k) in rn for k in keys) else 0.0

# 重新评分（用新 keys）
print("=== 三类 keys 重算（修正后 keys） ===")
from collections import Counter
for cat in ["情感表达", "条件判断", "编程语言"]:
    items = [x for x in results if x["cat"] == cat]
    ok = sum(score_keys(x["reply"], q2keys.get(x["q"], x["keys"])) for x in items)
    sem = sum(x["score_sem"] for x in items)
    print(f"{cat}: keys {ok:.0f}/{len(items)} ({ok/len(items)*100:.1f}%) | 语义 {sem:.0f}/{len(items)} ({sem/len(items)*100:.0f}%)")

# 剩余 keys 错题（确认无掩盖）
print("\n剩余 keys 错题（修正后仍不中 = 真弱答或漏词）:")
for cat in ["情感表达", "条件判断", "编程语言"]:
    items = [x for x in results if x["cat"] == cat]
    bad = [x for x in items if score_keys(x["reply"], q2keys.get(x["q"], x["keys"])) == 0]
    print(f"\n[{cat}] {len(bad)} 条:")
    for x in bad[:8]:
        print(f"  keys={q2keys.get(x['q'], x['keys'])} | {x['q'][:18]} → {x['reply'][:44]}")
