# -*- coding: utf-8 -*-
"""全量新测试集（176 题）基线跑测：找弱命中（llm 兜底）与错题。"""
import sys, os, json, re, time
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
data = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_full.json", encoding="utf-8"))["items"]

def norm(s):
    return re.sub(r"[\s^]", "", s or "").replace("²", "2").replace("³", "3")

results = []
t0 = time.time()
for i, item in enumerate(data, 1):
    q = item["q"]
    try:
        r = agent.chat(q, session_id=f"full-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as e:
        r, route, reply = {}, "err", f"ERR {e}"
    if item.get("objective") and item.get("keys"):
        s = 1.0 if any(norm(k) in norm(reply) for k in item["keys"]) else 0.0
    else:
        s = 1.0 if route in ("self", "llm") else 0.5
    results.append({**item, "route": route, "score": s, "reply": reply[:120]})
    if i % 40 == 0:
        print(f"[{i}/{len(data)}] {time.time()-t0:.0f}s", flush=True)

total = len(results)
correct = sum(x["score"] for x in results)
self_n = sum(1 for x in results if x["route"] == "self")
self_ok = sum(1 for x in results if x["route"] == "self" and x["score"] >= 0.5)
print(f"\n=== 全量基线: {correct:.0f}/{total} 总 {correct/total*100:.1f}% ===")
print(f"self 直答率: {self_ok}/{self_n} = {self_ok/self_n*100:.1f}% (self 占比 {self_n/total*100:.0f}%)")
rc = Counter(x["route"] for x in results)
print("route:", dict(rc))

by_src = defaultdict(lambda: [0, 0])
for x in results:
    src = x.get("source", "?")
    by_src[src.split("-")[0]][0] += x["score"]
    by_src[src.split("-")[0]][1] += 1
print("\n按来源:")
for s, (c, n) in sorted(by_src.items(), key=lambda x: -x[1][0]/x[1][1]):
    print(f"  {s}: {c:.0f}/{n} ({c/n*100:.1f}%)")

with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_full_results.json", "w", encoding="utf-8") as f:
    json.dump({"total": total, "correct": correct, "rate": correct/total,
               "self_n": self_n, "self_ok": self_ok,
               "results": results}, f, ensure_ascii=False, indent=1)
print("\n已存 new_testset_full_results.json")
agent.close()
