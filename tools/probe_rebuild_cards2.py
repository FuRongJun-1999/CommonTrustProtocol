# -*- coding: utf-8 -*-
"""探测剩余重建卡（第二轮 50 张之外的）：每卡 1 代表问题。"""
import json, sys, os, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
PROBES = [
    ("大学化学", "什么是摩尔？"), ("分子生物学", "什么是基因表达？"),
    ("化工原理", "什么是传热？"), ("分析化学", "什么是色谱法？"),
    ("固体物理", "什么是晶格？"), ("天体物理", "什么是中子星？"),
    ("复变函数", "什么是留数？"), ("实变函数", "什么是测度？"),
    ("常微分方程", "什么是欧拉方程？"), ("微分几何", "什么是测地线？"),
    ("原子物理", "什么是能级？"), ("工程制图", "什么是剖视图？"),
    ("土木工程基础", "什么是混凝土？"), ("工程学", "什么是疲劳破坏？"),
    ("会计学原理", "什么是资产负债表？"), ("市场营销", "什么是品牌定位？"),
    ("宏观经济学", "什么是通货膨胀？"), ("微观经济学", "什么是弹性？"),
    ("心理学", "什么是记忆巩固？"), ("医学", "什么是抗体？"),
    ("动物学", "什么是变态发育？"), ("微生物学", "什么是病毒？"),
    ("历史学", "什么是文艺复兴？"), ("地理学", "什么是洋流？"),
    ("哲学", "什么是存在主义？"), ("中国古代文学", "什么是宋词？"),
    ("中国现代文学", "什么是小说三要素？"), ("外国文学", "什么是浪漫主义？"),
    ("古代汉语", "什么是通假字？"), ("人类观察者", "什么是情绪管理？"),
]
results = []
t0 = time.time()
for i, (card, q) in enumerate(PROBES, 1):
    try:
        r = agent.chat(q, session_id=f"rebuild2-{i}")
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
for x in results:
    if x["route"] == "llm":
        print(f"  [{x['card']}] {x['q']} | reply: {x['reply'][:55]}")

with open(r"D:\Program Files\2_ai\knowledge-base\rebuild_probe2_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=1)
agent.close()
