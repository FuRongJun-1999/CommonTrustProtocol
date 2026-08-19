# -*- coding: utf-8 -*-
"""鲸鱼娘 100 轮长对话压力测试执行器。

同一 session 跑 100 轮，记录每轮 route/reply/时长，
结束后输出漂移分析与白箱边界统计。
"""
import sys, json, time, urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
BASE = "http://127.0.0.1:8793"
RID = "role-1787113781424"
SID = "whale-100"

turns = json.load(open(r"D:\Program Files\2_ai\knowledge-base\whale_100_turns.json", encoding="utf-8"))

def chat(msg, sid):
    body = json.dumps({"message": msg, "session_id": sid, "role_id": RID}).encode("utf-8")
    req = urllib.request.Request(BASE + "/api/chat", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))

results = []
t0 = time.time()
for i, t in enumerate(turns, 1):
    try:
        r = chat(t["q"], SID)
        reply = r.get("reply", "")
        route = r.get("route", "?")
        results.append({"round": i, "cat": t["cat"], "q": t["q"],
                        "route": route, "reply": reply})
    except Exception as e:
        results.append({"round": i, "cat": t["cat"], "q": t["q"],
                        "route": "err", "reply": f"ERR {e}"})
    if i % 20 == 0:
        elapsed = time.time() - t0
        print(f"[{i}/100] 用时 {elapsed:.0f}s 当前 route: {dict(Counter(x['route'] for x in results))}", flush=True)

total = time.time() - t0
print(f"\n=== 100 轮完成，总用时 {total:.0f}s（平均 {total/100:.1f}s/轮） ===")

# 保存结果
with open(r"D:\Program Files\2_ai\knowledge-base\whale_100_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("结果已存 whale_100_results.json")

# ---- 分析 ----
print("\n=== route 分布（白箱边界） ===")
rc = Counter(x["route"] for x in results)
print(f"  whitebox(白箱自处理): {rc.get('whitebox', 0)} 轮 ({rc.get('whitebox',0)/100:.0%})")
print(f"  llm(LLM兜底): {rc.get('llm', 0)} 轮 ({rc.get('llm',0)/100:.0%})")
print(f"  err: {rc.get('err', 0)} 轮")

# 按类别 route
print("\n=== 按类别 route ===")
by_cat = {}
for x in results:
    by_cat.setdefault(x["cat"], []).append(x["route"])
for cat, routes in by_cat.items():
    wb = routes.count("whitebox")
    print(f"  {cat}: whitebox {wb}/{len(routes)} ({wb/len(routes):.0%})")

# ---- 漂移检测 ----
print("\n=== 漂移检测 ===")
flags = []
for x in results:
    reply = x["reply"]
    issues = []
    if "灵枢" in reply and "我是灵枢" in reply:
        issues.append("身份泄漏(我是灵枢)")
    if "程序" in reply or "AI" in reply.lower():
        issues.append("跳出角色(程序/AI)")
    if "查资料" in reply or "搜索" in reply:
        issues.append("工具性回答")
    if x["route"] == "err":
        issues.append("错误")
    if issues:
        flags.append({"round": x["round"], "cat": x["cat"], "q": x["q"],
                      "issues": issues, "reply": reply[:60]})
if flags:
    print(f"发现 {len(flags)} 处漂移/异常:")
    for f in flags:
        print(f"  [{f['round']}] ({f['cat']}) {f['q']}")
        print(f"    ⚠️ {','.join(f['issues'])} → {f['reply']}")
else:
    print("✓ 零漂移/零异常")

# ---- 机械重复检测（相邻轮回复相似度） ----
print("\n=== 机械重复检测 ===")
def norm(s):
    import re
    return re.sub(r"[^\u4e00-\u9fff]", "", s)
dups = []
for i in range(1, len(results)):
    if results[i]["route"] == "err" or results[i-1]["route"] == "err":
        continue
    a, b = norm(results[i-1]["reply"]), norm(results[i]["reply"])
    if a and b and (a == b or (len(set(a) & set(b)) / max(len(set(a)), 1) > 0.9)):
        dups.append((results[i]["round"], results[i-1]["round"]))
if dups:
    print(f"相邻轮高度重复 {len(dups)} 处: {dups[:5]}")
else:
    print("✓ 无机械重复")

print("\n=== 测试完成 ===")
