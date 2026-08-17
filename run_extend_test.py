# -*- coding: utf-8 -*-
"""跑 110 题扩展测试：评分 + route 记录，输出弱项分析"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')

from extend_test_100 import QUESTIONS
from aeis.api import Agent

agent = Agent(identity="灵枢",
              db_path=r'C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db')

import re as _re

def score(reply, keys):
    """评分：规范化后关键词匹配（去空格/^幂、上下标转普通字符）。"""
    r = reply or ""
    rn = _re.sub(r"[\s^]", "", r).replace("²", "2").replace("³", "3").replace("√", "")
    kn = [_re.sub(r"[\s^]", "", k).replace("²", "2").replace("³", "3") for k in keys]
    return 1.0 if any(k in r or k in rn for k in kn) else 0.0

results = []
for i, (q, keys, cat) in enumerate(QUESTIONS, 1):
    try:
        r = agent.chat(q, session_id="extend_110")
        reply = r.get("reply", "")
        route = r.get("route", "?")
    except Exception as e:
        reply = f"ERR {e}"
        route = "err"
    s = score(reply, keys)
    results.append({"q": q, "keys": keys, "cat": cat, "reply": reply,
                    "route": route, "score": s})
    if i % 20 == 0 or s == 0:
        print(f"[{i:>3}] {'✓' if s else '✗'} [{cat}] {q[:26]} | route={route}")
        if s == 0:
            print(f"       → {reply[:90]}")

total = len(results)
correct = sum(r["score"] for r in results)
print(f"\n=== 结果: {correct:.0f}/{total} ({correct/total*100:.0f}%) ===")

# 按类别统计
from collections import defaultdict
cat_stats = defaultdict(lambda: [0, 0])  # cat -> [correct, total]
for r in results:
    cat_stats[r["cat"]][0] += r["score"]
    cat_stats[r["cat"]][1] += 1
print("\n=== 按类别 ===")
for cat, (c, t) in sorted(cat_stats.items(), key=lambda x: -x[1][0]/x[1][1]):
    print(f"  {cat:<5} {c:.0f}/{t} ({c/t*100:.0f}%)")

# route 分布
from collections import Counter
rc = Counter(r["route"] for r in results)
print(f"\nroute 分布: {dict(rc)}")

# 保存结果
import json
with open(r"D:\Program Files\2_ai\knowledge-base\extend_110_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\n结果已存 extend_110_results.json")
agent.close()
