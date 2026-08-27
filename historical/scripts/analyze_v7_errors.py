# -*- coding: utf-8 -*-
"""分析 dialogue_1000 v7 结果（knowledge-base 最新版）：错题提取 + 达标复核。"""
import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

path = r"D:\Program Files\2_ai\knowledge-base\dialogue_1000_results_maindb.json"
results = json.load(open(path, encoding="utf-8"))
print("总题数:", len(results))
print("结构样例 keys:", list(results[0].keys()))

rc = Counter(x.get("route") for x in results)
print("route 分布:", dict(rc))

# self 直答正确率
self_total = self_correct = 0
for x in results:
    if x.get("route") == "self":
        self_total += 1
        if x.get("score", 0) >= 0.5:
            self_correct += 1
print(f"self: {self_correct}/{self_total} = {self_correct/self_total:.2%}")

# 总正确率
ok = sum(1 for x in results if x.get("score", 0) >= 0.5)
print(f"总正确: {ok}/{len(results)} = {ok/len(results):.2%}")

# 错题
wrong = [(i, x) for i, x in enumerate(results) if x.get("score", 0) < 0.5]
print(f"\n错题总数: {len(wrong)}")
by_route = Counter(x[1].get("route") for x in wrong)
print("错题 route 分布:", dict(by_route))

print("\n=== 错题清单（去重）===")
seen = set()
for i, x in wrong:
    q = x.get("q", "")
    key = q
    if key in seen:
        continue
    seen.add(key)
    print(f"[{i}] {x.get('route')} | {q[:70]}")
    print(f"    reply: {x.get('reply','')[:80]}")
print(f"\n去重后唯一错题数: {len(seen)}")
