# -*- coding: utf-8 -*-
"""矛盾测试集 v38 运行：6 题 → 定位断裂。"""
import sys, os, json
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
data = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v38.json", encoding="utf-8"))["items"]
BAD_SIGNALS = ["Let me", "Actually,", "I think", "I should", "Since the",
               "The knowledge", "This is", "I'll", "So I", "In the context",
               "I want", "Let's", "I'm", "I would", "I can", "I need"]

results = []
for i, item in enumerate(data, 1):
    q = item["q"]
    try:
        r = agent.chat(q, session_id=f"cv38-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as e:
        route, reply = "err", f"ERR {e}"
    bad = route in ("llm", "err", "self_fallback")
    if not bad:
        bad = any(s in reply for s in BAD_SIGNALS)
    if not bad and len(reply) < 15:
        bad = True
    if not bad and "内容安全拦截" in reply:
        bad = True
    results.append({**item, "route": route, "bad": bad, "reply": reply[:100]})
    mark = "✗" if bad else "✓"
    print(f"[{mark}] ({item['domain']}/{item['stage']}) {q[:30]} | {route}", flush=True)

total = len(results)
ok = sum(1 for x in results if not x["bad"])
print(f"\n=== v38: {ok}/{total} ({ok/total*100:.0f}%) ===")
print("route:", dict(Counter(x["route"] for x in results)))
print("=== 断裂清单 ===")
for x in results:
    if x["bad"]:
        print(f"  [{x['domain']}/{x['stage']}] {x['q'][:34]} | {x['route']} | {(x['reply'] or '')[:40]}")
with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v38_results.json", "w", encoding="utf-8") as f:
    json.dump({"total": total, "ok": ok, "results": results}, f, ensure_ascii=False, indent=1)
print("已存 conflict_testset_v38_results.json")
agent.close()
