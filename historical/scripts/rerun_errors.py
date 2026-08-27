# -*- coding: utf-8 -*-
"""错题复测集验证（v1.26 · 持续学习流程第二步）

对 v7 的 12 道错题在当前图谱（最新补卡后）复测：
  - 走完整对话链路（agent.chat）
  - 统计 self 直答/llm 兜底/正确率
  - 对比 v7：验证补卡是否根治（错题变对 = 根治；仍错 = 未覆盖）

判定（与 v7 一致）：
  - objective=True 题：reply 含 keys 任一 → 1.0
  - 其余：route in (self, llm) → 1.0（对话类按路由兜底）
"""
import sys, os, json, re, time
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
KB = r"D:\Program Files\2_ai\knowledge-base"
# 白箱/图谱运行时路径（site-packages 优先，同 run_dialogue_1000_maindb.py）
for _p in (r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages",
           os.path.join(KB, "wisdom")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ.get("AEIS_DB", ":memory:"))

errors = json.load(open(os.path.join(
    KB, "recognized_sets",
    "dialogue_1000_v7_rerun_errors.json"), encoding="utf-8"))
# 关联原题库的 cat/objective/keys
full = {x["q"]: x for x in json.load(
    open(os.path.join(KB, "dialogue_1000.json"), encoding="utf-8"))}


def norm(s):
    return re.sub(r"[\s^]", "", s or "").replace("²", "2").replace("³", "3")


results = []
t0 = time.time()
for i, e in enumerate(errors, 1):
    q = e["q"]
    src = full.get(q, {})
    try:
        # v1.26 修复：每题独立 session——共用 session 会让搜索计数器累积
        # （「本会话已搜索 7 次」）误触发搜索收敛拒绝，污染后续题
        r = agent.chat(q, session_id=f"rerun-err-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as ex:
        r, route, reply = {}, "err", f"ERR {ex}"
    if src.get("objective"):
        s = 1.0 if any(norm(k) in norm(reply) for k in src.get("keys", [])) else 0.0
    else:
        s = 1.0 if route in ("self", "llm") else 0.5
    results.append({"q": q, "v7_route": e["v7_route"], "route": route,
                    "score": s, "reply": reply[:220]})
    print(f"[{i}/{len(errors)}] {q[:36]} | v7={e['v7_route']} now={route} "
          f"score={s} ({time.time()-t0:.0f}s)", flush=True)

print(f"\n=== 复测完成: {sum(x['score'] for x in results):.0f}/{len(results)} "
      f"({sum(x['score'] for x in results)/len(results)*100:.1f}%) ===")
rc = Counter(x["route"] for x in results)
print("route:", dict(rc))
print("\n逐题详情:")
for x in results:
    mark = "✓" if x["score"] >= 0.5 else "✗"
    print(f"{mark} [{x['route']}] {x['q'][:40]}")
    print(f"    reply: {x['reply'][:100]}")

with open(os.path.join(KB, "recognized_sets",
                       "dialogue_1000_v7_rerun_results.json"), "w",
          encoding="utf-8") as f:
    json.dump({"n": len(results),
               "correct": sum(x["score"] for x in results),
               "results": results}, f, ensure_ascii=False, indent=1)
print("\n已存 recognized_sets/dialogue_1000_v7_rerun_results.json")
agent.close()
