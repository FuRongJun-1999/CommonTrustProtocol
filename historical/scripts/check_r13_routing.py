# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
qs = [
    ("感冒", "为什么天冷容易感冒？"),
    ("感冒", "感冒是怎么来的？"),
    ("感冒", "感冒不吃药能好吗？"),
    ("感冒", "受凉为什么会感冒？"),
    ("感冒", "怎么预防感冒？"),
    ("感冒", "感冒和流感有什么区别？"),
    ("光合作用", "叶子为什么是绿的？"),
    ("光合作用", "植物为什么要晒太阳？"),
    ("光合作用", "光合作用产生了什么？"),
    ("光合作用", "植物晚上也进行光合作用吗？"),
    ("遗传", "为什么孩子长得像父母？"),
    ("遗传", "兄弟姐妹为什么长得不一样？"),
    ("遗传", "遗传决定一切吗？"),
    ("萌发", "为什么种子浇水就会发芽？"),
    ("萌发", "种子发芽需要什么条件？"),
    ("萌发", "为什么有的种子不发芽？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="r13-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:44].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
