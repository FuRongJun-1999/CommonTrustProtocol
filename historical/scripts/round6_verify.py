# -*- coding: utf-8 -*-
"""round6 固定变体验证（完整路由）"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

data = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_r6.json", encoding="utf-8"))
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
TOTAL = 0
HIT = 0
for theme, variants in data["themes"].items():
    n = len(variants)
    ok = 0
    for i, v in enumerate(variants, 1):
        r = agent.chat(v, session_id=f"r6-{i}")
        reply = r.get("reply", "")
        hit = r.get("route") == "self" and len(reply) > 60
        if hit:
            ok += 1
    print(f"{theme}: {ok}/{n}")
    TOTAL += n
    HIT += ok
print(f"=== 总计: {HIT}/{TOTAL} ({HIT/TOTAL*100:.0f}%) ===")
agent.close()
