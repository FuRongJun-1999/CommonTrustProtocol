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
    ("化学变化", "什么是化学变化？"),
    ("化学变化", "铁生锈是什么变化？"),
    ("化学变化", "化学变化和物理变化什么区别？"),
    ("中和反应", "什么是中和反应？"),
    ("中和反应", "为什么胃酸过多要吃药？"),
    ("中和反应", "蚊虫叮咬怎么处理？"),
    ("催化剂", "催化剂是什么？"),
    ("催化剂", "催化剂会消耗吗？"),
    ("催化剂", "生活里有哪些催化剂？"),
    ("元素周期律", "什么是元素周期律？"),
    ("元素周期律", "周期表怎么排的？"),
    ("元素周期律", "同一族性质相似吗？"),
    ("燃烧条件", "燃烧需要哪三个条件？"),
    ("燃烧条件", "为什么水能灭火？"),
    ("燃烧条件", "为什么有的东西点不着？"),
    ("盐水融雪", "为什么撒盐雪就化了？"),
    ("盐水融雪", "盐水为什么不容易结冰？"),
    ("盐水融雪", "融雪剂是什么？"),
    ("糖盐味道", "为什么糖是甜的盐是咸的？"),
    ("糖盐味道", "糖和盐一样吗？"),
    ("蜂蜜防腐", "为什么蜂蜜放很久不会坏？"),
    ("蜂蜜防腐", "蜂蜜结晶是坏了吗？"),
    ("蜂蜜防腐", "蜂蜜会变质吗？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c2-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:40].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
