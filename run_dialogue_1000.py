# -*- coding: utf-8 -*-
"""跑 1000 条日常对话测试：客观题关键词评分 + 主观题通路匹配"""
import sys, os, json, re, time
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')

from aeis.api import Agent

# 可复现：默认 :memory:（临时记忆），智慧之书随包加载（aeis/wisdom 138+ 卡）；
# 可用 AEIS_DB 指定持久库（复现者无需本机 db）
agent = Agent(identity="灵枢", db_path=os.environ.get("AEIS_DB", ":memory:"))

data = json.load(open(os.path.join(HERE, "dialogue_1000.json"), encoding="utf-8"))

def norm(s):
    return re.sub(r"[\s^]", "", s or "").replace("²","2").replace("³","3")

def score_obj(reply, keys):
    rn = norm(reply)
    return 1.0 if any(norm(k) in rn for k in keys) else 0.0

def score_subj(cat, r):
    """主观题通路匹配：类型 → 期望的路由/字段。"""
    route = r.get("route")
    if r.get("blocked"):
        return 0.0
    if cat == "情感表达":
        return 1.0 if (r.get("emotion") or route in ("self",)) else 0.5
    if cat == "日常闲聊":
        return 1.0 if (r.get("chitchat") or route in ("self",)) else 0.5
    if cat == "诚实边界":
        return 1.0 if r.get("honest_kind") or r.get("honest") else 0.5
    if cat in ("意见请求", "场景对话"):
        # 有实质回应即可（不空洞、不报错）
        reply = (r.get("reply") or "")
        return 1.0 if len(reply) > 8 and "引擎未就绪" not in reply else 0.0
    return 1.0 if route in ("self", "llm") else 0.5

results = []
t0 = time.time()
for i, item in enumerate(data, 1):
    try:
        r = agent.chat(item["q"], session_id="dialogue1000")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as e:
        r, route, reply = {}, "err", f"ERR {e}"
    if item["objective"]:
        s = score_obj(reply, item["keys"])
    else:
        s = score_subj(item["cat"], r)
    results.append({**item, "reply": reply, "route": route, "score": s})
    if i % 100 == 0:
        el = time.time() - t0
        print(f"[{i}/1000] 用时 {el:.0f}s ({el/i:.2f}s/条) 当前累计正确率 {sum(x['score'] for x in results)/i*100:.1f}%", flush=True)

total = len(results)
correct = sum(x["score"] for x in results)
print(f"\n=== 1000 条完成: {correct:.0f}/{total} ({correct/total*100:.1f}%) 用时 {time.time()-t0:.0f}s ===")

# 按类别
from collections import defaultdict
cat_stats = defaultdict(lambda: [0, 0])
route_cnt = defaultdict(int)
for x in results:
    cat_stats[x["cat"]][0] += x["score"]
    cat_stats[x["cat"]][1] += 1
    route_cnt[x["route"]] += 1
print("\n按类别:")
for c, (s, t) in sorted(cat_stats.items(), key=lambda x: -x[1][0]/x[1][1]):
    print(f"  {c:<6} {s:.0f}/{t} ({s/t*100:.1f}%)")
print(f"\nroute 分布: {dict(route_cnt)}")

with open(r"D:\Program Files\2_ai\knowledge-base\dialogue_1000_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("已存 dialogue_1000_results.json")
agent.close()
