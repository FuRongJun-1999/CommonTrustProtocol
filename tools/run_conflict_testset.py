# -*- coding: utf-8 -*-
"""矛盾测试集基线：49 题正反合链跑白箱 → 找断裂环节。

断裂 = route=llm / 纯导航 / 英文残留 / 答非所问——矛盾发展的
某个阶段白箱接不住，就是真盲区。
"""
import sys, os, json, re, time
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
data = json.load(open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v1.json", encoding="utf-8"))["items"]

# 判定：坏回答信号（导航无实质/英文残留/答非所问）
# v1 修复：这些是「实质回答+导航尾巴」误报——严格管教等答了实质内容
# 但尾部带「这个可以看」。真正坏 = 无实质内容（纯导航开头）或英文残留。
BAD_SIGNALS = ["Let me", "Actually,", "I think", "I should", "Since the",
               "The knowledge", "This is", "I'll", "So I", "In the context",
               "I want", "Let's", "I'm", "I would", "I can", "I need"]

results = []
t0 = time.time()
for i, item in enumerate(data, 1):
    q = item["q"]
    try:
        r = agent.chat(q, session_id=f"conf-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as e:
        route, reply = "err", f"ERR {e}"
    # 判定质量：route=llm 或英文残留 = 断裂；纯导航（无实质答案）= 断裂
    bad = route in ("llm", "err", "self_fallback")
    if not bad:
        bad = any(s in reply for s in BAD_SIGNALS)
    # 纯导航：「你说的这个，可以看」开头 = 无实质答案
    if not bad and reply.startswith("你说的这个，可以看"):
        bad = True
    # 导航式反问（这个问题…）+ 无实质 = 断裂
    if not bad and len(reply) < 15:
        bad = True
    results.append({**item, "route": route, "bad": bad, "reply": reply[:120]})
    mark = "✗" if bad else "✓"
    print(f"[{mark}] ({item['stage']}) {q[:34]} -> {route}", flush=True)

print(f"\n=== 矛盾测试集基线: {sum(1 for x in results if not x['bad'])}/{len(results)} 合格 ===")
rc = Counter(x["route"] for x in results)
print("route:", dict(rc))

# 按矛盾域+阶段分析
by_domain = defaultdict(lambda: [0, 0])
by_stage = defaultdict(lambda: [0, 0])
for x in results:
    by_domain[x["domain"]][0] += 0 if x["bad"] else 1
    by_domain[x["domain"]][1] += 1
    by_stage[x["stage"]][0] += 0 if x["bad"] else 1
    by_stage[x["stage"]][1] += 1
print("\n按域:")
for d, (ok, n) in sorted(by_domain.items(), key=lambda x: x[1][0]/x[1][1]):
    print(f"  {d}: {ok}/{n} ({ok/n*100:.0f}%)")
print("\n按阶段（正反合）:")
for s, (ok, n) in sorted(by_stage.items(), key=lambda x: -x[1][1]):
    print(f"  {s}: {ok}/{n} ({ok/n*100:.0f}%)")

print("\n=== 断裂清单（盲区）===")
for x in results:
    if x["bad"]:
        print(f"  [{x['domain']}/{x['stage']}] {x['q'][:40]}")
        print(f"    route={x['route']} reply: {x['reply'][:70]}")

with open(r"D:\Program Files\2_ai\knowledge-base\conflict_testset_v1_results.json", "w", encoding="utf-8") as f:
    json.dump({"total": len(results), "ok": sum(1 for x in results if not x["bad"]),
               "results": results}, f, ensure_ascii=False, indent=1)
print("\n已存 conflict_testset_v1_results.json")
agent.close()
