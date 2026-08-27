# -*- coding: utf-8 -*-
"""固定自然问法测试集验证（fp 优先 + 自然表达触发词 patch 后）"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as _st
from aeis.api import Agent

data = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_r5.json", encoding="utf-8"))
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])

for theme, cfg in data["themes"].items():
    variants = cfg["variants"]
    fp_hits = sum(1 for v in variants if theme in _st.encode(v))
    # 完整路由（含 layered）
    full = 0
    print(f"=== {theme} ===")
    for i, v in enumerate(variants, 1):
        r = agent.chat(v, session_id=f"r5-{i}")
        route = r.get("route", "?")
        reply = r.get("reply", "")
        # 主题直答特征：reply 是否含主题相关（用簇名或关键内容）
        hit = route == "self" and (theme in reply or len(reply) > 60)
        if hit:
            full += 1
        print(f"  [{'✓' if hit else '✗'}] {v[:26]}")
    print(f"  fp命中: {fp_hits}/{len(variants)} | 完整路由命中: {full}/{len(variants)}")
agent.close()
