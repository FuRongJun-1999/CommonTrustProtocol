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
    ("燃烧", "为什么纸遇到火会烧起来？"),
    ("燃烧", "灭火为什么要用水？"),
    ("燃烧", "为什么有的东西点不着？"),
    ("燃烧", "燃烧和生锈一样吗？"),
    ("溶解", "为什么糖放进水里会不见？"),
    ("溶解", "盐放进菜里菜为什么变咸？"),
    ("溶解", "溶解和融化一样吗？"),
    ("溶解", "热水为什么溶解更快？"),
    ("汽水气泡", "为什么打开汽水会冒泡？"),
    ("汽水气泡", "汽水里的气泡是什么？"),
    ("汽水气泡", "为什么汽水放久了没气？"),
    ("汽水气泡", "为什么喝汽水会打嗝？"),
    ("血液循环", "为什么运动后心跳会变快？"),
    ("血液循环", "心脏是干什么的？"),
    ("血液循环", "为什么心跳有快慢？"),
    ("血液循环", "怎么让心脏更健康？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="r14-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:44].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
