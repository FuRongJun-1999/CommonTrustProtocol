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
    ("供需求", "为什么供大于求会降价？"),
    ("供需求", "为什么供不应求会涨价？"),
    ("供需求", "价格是怎么定的？"),
    ("通货膨胀", "通货膨胀是什么？"),
    ("通货膨胀", "为什么钱越来越不值钱？"),
    ("通货膨胀", "怎么应对通货膨胀？"),
    ("机会成本", "什么是机会成本？"),
    ("机会成本", "机会成本怎么算？"),
    ("机会成本", "机会成本和沉没成本什么区别？"),
    ("二进制", "二进制是什么？"),
    ("二进制", "为什么计算机用二进制？"),
    ("二进制", "一个字节是什么？"),
    ("数据库", "数据库是什么？"),
    ("数据库", "怎么查数据库的数据？"),
    ("数据库", "数据库和Excel什么区别？"),
    ("递归", "什么是递归？"),
    ("递归", "递归为什么要终止条件？"),
    ("递归", "递归和循环什么区别？"),
    ("面向对象", "什么是面向对象？"),
    ("面向对象", "类和对象什么关系？"),
    ("面向对象", "面向对象和面向过程什么区别？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c6-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:36].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
