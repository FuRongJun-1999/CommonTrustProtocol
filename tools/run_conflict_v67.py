# -*- coding: utf-8 -*-
"""矛盾测试集 v64：学科常识 12 簇（c15）24 题"""
import sys, os, json, time
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
data = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v67.json", encoding="utf-8"))["items"]
BAD_SIGNALS = ["Let me", "Actually,", "I think", "I should", "Since the",
               "The knowledge", "This is", "I'll", "So I", "In the context",
               "I want", "Let's", "I'm", "I would", "I can", "I need"]

results = []
for i, item in enumerate(data, 1):
    q = item["q"]
    try:
        r = agent.chat(q, session_id=f"cvv67-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as e:
        route, reply = "err", f"ERR {e}"
    bad = route in ("llm", "err", "self_fallback")
    if not bad:
        bad = any(s in reply for s in BAD_SIGNALS)
    if not bad and reply.startswith("你说的这个，可以看"):
        bad = True
    if not bad and len(reply) < 15:
        bad = True
    results.append({**item, "route": route, "bad": bad, "reply": reply[:110]})
    mark = "✗" if bad else "✓"
    print(f"[{mark}] ({item['domain']}/{item['stage']}) {q[:30]}", flush=True)

total = len(results)
ok = sum(1 for x in results if not x["bad"])
print(f"\n=== v67 基线: {ok}/{total} ({ok/total*100:.0f}%) ===")
rc = Counter(x["route"] for x in results)
print("route:", dict(rc))
by_domain = defaultdict(lambda: [0, 0])
by_stage = defaultdict(lambda: [0, 0])
for x in results:
    by_domain[x["domain"]][0] += 0 if x["bad"] else 1
    by_domain[x["domain"]][1] += 1
    by_stage[x["stage"]][0] += 0 if x["bad"] else 1
    by_stage[x["stage"]][1] += 1
print("\n按域:")
for d, (o, n) in sorted(by_domain.items(), key=lambda x: x[1][0] / x[1][1]):
    print(f"  {d}: {o}/{n} ({o/n*100:.0f}%)")
print("\n按阶段:")
for s, (o, n) in sorted(by_stage.items(), key=lambda x: x[1][1]):
    print(f"  {s}: {o}/{n} ({o/n*100:.0f}%)")
print("\n=== 断裂清单 ===")
for x in results:
    if x["bad"]:
        print(f"  [{x['domain']}/{x['stage']}] {x['q'][:34]} | {x['route']}")

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v67_results.json", "w", encoding="utf-8") as f:
    json.dump({"total": total, "ok": ok, "results": results}, f, ensure_ascii=False, indent=1)
print("\n已存 conflict_testset_v67_results.json")
agent.close()
