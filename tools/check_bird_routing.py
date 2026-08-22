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
    "为什么鸟能飞行，人不行？",
    "为什么鸟能飞？",
    "鸟是怎么飞的？",
    "鸟为什么会飞？",
    "人为什么不能像鸟一样飞？",
    "翅膀是怎么产生升力的？",
    "鸟的羽毛有什么用？",
    "为什么鸟的身体那么轻？",
    "为什么鸵鸟有翅膀却飞不起来？",
    "为什么人会飞不起来？",
    "怎么让鸟飞起来？",
    "为什么鸟能在天上盘旋？",
]
ok = 0
for q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="bird-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = "鸟的飞行" in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {q}")
    print(f"   fp={keys} route={route} | {reply[:44].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
