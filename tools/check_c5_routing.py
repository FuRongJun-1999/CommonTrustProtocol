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
    ("一般现在时", "一般现在时怎么用？"),
    ("一般现在时", "什么时候动词加s？"),
    ("一般现在时", "一般现在时怎么变否定？"),
    ("被动语态", "什么是被动语态？"),
    ("被动语态", "被动语态怎么构成？"),
    ("被动语态", "什么时候用被动语态？"),
    ("名词复数", "名词复数怎么变？"),
    ("名词复数", "名词复数有什么特殊？"),
    ("名词复数", "可数名词和不可数名词什么区别？"),
    ("比较级", "比较级怎么变？"),
    ("比较级", "为什么有的加er有的用more？"),
    ("比较级", "比较级和最高级什么区别？"),
    ("定语从句", "什么是定语从句？"),
    ("定语从句", "关系词怎么选？"),
    ("定语从句", "that和which什么区别？"),
    ("英语时态", "英语时态有哪些？"),
    ("英语时态", "时态表示什么？"),
    ("英语时态", "现在完成时怎么用？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c5-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:36].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
