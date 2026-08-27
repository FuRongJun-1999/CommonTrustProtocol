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
    ("发酵", "为什么面团会发酵？"),
    ("发酵", "馒头为什么松软？"),
    ("发酵", "酵母是什么？"),
    ("发酵", "面发不起来怎么办？"),
    ("发酵", "发酵需要什么条件？"),
    ("发酵", "酸奶是怎么做出来的？"),
    ("发酵", "发面和发霉有什么区别？"),
    ("氧化", "为什么铁会生锈？"),
    ("氧化", "菜刀放久了为什么有锈？"),
    ("氧化", "为什么潮湿的地方铁锈得快？"),
    ("氧化", "为什么有的铁不生锈？"),
    ("氧化", "怎么防生锈？"),
    ("氧化", "为什么苹果切开会发黄？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="r12-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:44].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
