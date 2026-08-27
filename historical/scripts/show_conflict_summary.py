# -*- coding: utf-8 -*-
import json, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding="utf-8")
d = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v1_results.json", encoding="utf-8"))
print(f"总: {d['ok']}/{d['total']} 合格 ({d['ok']/d['total']*100:.0f}%)")
by_domain = defaultdict(lambda: [0, 0])
by_stage = defaultdict(lambda: [0, 0])
for x in d["results"]:
    by_domain[x["domain"]][0] += 0 if x["bad"] else 1
    by_domain[x["domain"]][1] += 1
    by_stage[x["stage"]][0] += 0 if x["bad"] else 1
    by_stage[x["stage"]][1] += 1
print("\n按域:")
for dom, (ok, n) in sorted(by_domain.items(), key=lambda x: x[1][0]/x[1][1]):
    print(f"  {dom}: {ok}/{n} ({ok/n*100:.0f}%)")
print("\n按阶段:")
for s, (ok, n) in sorted(by_stage.items(), key=lambda x: x[1][1]):
    print(f"  {s}: {ok}/{n} ({ok/n*100:.0f}%)")
print("\n=== 全部断裂 ===")
for x in d["results"]:
    if x["bad"]:
        print(f"  [{x['domain']}/{x['stage']}] {x['q'][:38]}")
