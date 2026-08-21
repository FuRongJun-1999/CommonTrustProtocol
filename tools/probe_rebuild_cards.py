# -*- coding: utf-8 -*-
"""宽泛重建卡探测：每卡 1 个代表问题 → 找出 llm 兜底（静默盲区）。"""
import json, sys, os, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])

PROBES = [
    ("中国古代文学", "什么是唐诗？"), ("中国现代文学", "什么是鲁迅的散文？"),
    ("人工智能", "什么是机器学习？"), ("人类观察者", "什么是人类观察者？"),
    ("会计学原理", "什么是借贷记账法？"), ("分子生物学", "什么是DNA复制？"),
    ("分析化学", "什么是滴定分析？"), ("初中化学", "什么是化学方程式？"),
    ("初中历史", "什么是秦朝统一？"), ("初中地理", "什么是季风气候？"),
    ("初中数学", "什么是因式分解？"), ("初中物理", "什么是杠杆原理？"),
    ("初中生物", "什么是细胞分裂？"), ("初中英语", "什么是现在完成时？"),
    ("初中语文", "什么是修辞手法？"), ("初中道德与法治", "什么是社会主义核心价值观？"),
    ("动物学", "什么是哺乳动物？"), ("化学", "什么是化学键？"),
    ("化工原理", "什么是精馏？"), ("医学", "什么是免疫系统？"),
    ("历史学", "什么是历史唯物主义？"), ("原子物理", "什么是放射性衰变？"),
    ("古代汉语", "什么是文言文？"), ("哲学", "什么是辩证法？"),
    ("固体物理", "什么是能带？"), ("土木工程基础", "什么是梁的弯曲？"),
    ("地理学", "什么是板块构造？"), ("复变函数", "什么是解析函数？"),
    ("外国文学", "什么是莎士比亚悲剧？"), ("大学化学", "什么是热力学第一定律？"),
    ("大学思政", "什么是唯物史观？"), ("大学物理", "什么是电磁感应？"),
    ("大学英语", "什么是定语从句？"), ("天体物理", "什么是黑洞？"),
    ("天文学", "什么是恒星演化？"), ("宏观经济学", "什么是GDP？"),
    ("实变函数", "什么是勒贝格积分？"), ("小学数学", "什么是分数？"),
    ("小学科学", "什么是光合作用？"), ("小学英语", "什么是音标？"),
    ("小学语文", "什么是古诗？"), ("小学道德与法治", "什么是诚实守信？"),
    ("工程制图", "什么是三视图？"), ("工程学", "什么是应力？"),
    ("市场营销", "什么是市场细分？"), ("常微分方程", "什么是可分离变量方程？"),
    ("微分几何", "什么是曲率？"), ("微生物学", "什么是细菌？"),
    ("微观经济学", "什么是供需曲线？"), ("心理学", "什么是经典条件反射？"),
]

results = []
t0 = time.time()
for i, (card, q) in enumerate(PROBES, 1):
    try:
        r = agent.chat(q, session_id=f"rebuild-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
    except Exception as e:
        route, reply = "err", f"ERR {e}"
    results.append({"card": card, "q": q, "route": route, "reply": reply[:100]})
    mark = "S" if route == "self" else "L"
    print(f"[{mark}] {card}: {q[:22]} -> {route}", flush=True)

print(f"\n=== 探测完成 ({time.time()-t0:.0f}s) ===")
llm_n = sum(1 for x in results if x["route"] == "llm")
print(f"llm 兜底: {llm_n}/{len(results)}")
print("\n=== llm 兜底清单（静默盲区）===")
for x in results:
    if x["route"] == "llm":
        print(f"  [{x['card']}] {x['q']} | reply: {x['reply'][:60]}")

with open(r"D:\Program Files\2_ai\knowledge-base\rebuild_probe_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
agent.close()
