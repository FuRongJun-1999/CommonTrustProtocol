# -*- coding: utf-8 -*-
"""三类专项重测（情感表达/条件判断/编程语言）v1.17 代码
与 dialogue_1000_maindb 同路径（Agent.chat），输出三分类语义+keys双评分。"""
import sys, os, json, re, time
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')

from aeis.api import Agent

agent = Agent(identity="灵枢",
              db_path=r'C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db')

data = json.load(open(os.path.join(HERE, "three_cats_test.json"), encoding="utf-8"))

def norm(s):
    return re.sub(r"[\s^]", "", s or "")

def score_keys(reply, keys):
    rn = norm(reply)
    return 1.0 if any(norm(k) in rn for k in keys) else 0.0

def semantic_ok(cat, reply):
    r = norm(reply)
    if cat == "情感表达":
        return len(r) > 15
    if cat == "条件判断":
        if "基于条件空间理解世界" in r or "不给绝对答案" in r:
            return False
        return len(r) > 15
    if cat == "编程语言":
        prog = ("函数", "递归", "循环", "线程", "GIL", "编译", "变量", "调试",
                "程序", "代码", "算法", "对象", "类", "封装", "继承", "多态",
                "语法", "类型", "指针", "内存", "并发")
        return any(p in r for p in prog)
    return False

results = []
t0 = time.time()
for cat, items in data.items():
    for item in items:
        try:
            r = agent.chat(item["q"], session_id="threecats")
            reply = r.get("reply", "")
            route = r.get("route", "?")
        except Exception as e:
            reply, route = f"ERR {e}", "err"
        sk = score_keys(reply, item["keys"])
        sem = 1.0 if semantic_ok(cat, reply) else 0.0
        results.append({"cat": cat, "q": item["q"], "keys": item["keys"],
                        "reply": reply, "route": route, "score_keys": sk,
                        "score_sem": sem})
    print(f"[{cat}] 完成，累计 {time.time()-t0:.0f}s", flush=True)

# 汇总
print("\n=== 三类重测（v1.17 代码） ===")
for cat in ["情感表达", "条件判断", "编程语言"]:
    items = [x for x in results if x["cat"] == cat]
    k_ok = sum(x["score_keys"] for x in items)
    s_ok = sum(x["score_sem"] for x in items)
    rc = Counter(x["route"] for x in items)
    print(f"{cat}: keys评分 {k_ok:.0f}/{len(items)} ({k_ok/len(items)*100:.1f}%) | "
          f"语义评分 {s_ok:.0f}/{len(items)} ({s_ok/len(items)*100:.1f}%) | route {dict(rc)}")

# 错题明细（语义也错的）
print("\n=== 语义错题（真缺陷） ===")
for cat in ["条件判断", "编程语言", "情感表达"]:
    bad = [x for x in results if x["cat"] == cat and x["score_sem"] == 0]
    if bad:
        print(f"\n[{cat}] {len(bad)} 条:")
        for x in bad:
            print(f"  [{x['route']}] {x['q'][:24]} → {x['reply'][:60]}")

with open(os.path.join(HERE, "three_cats_results_v17.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
print("\n已存 three_cats_results_v17.json")
agent.close()
