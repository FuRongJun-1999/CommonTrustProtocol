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
    ("等高线", "等高线是什么？"),
    ("等高线", "等高线怎么看地形？"),
    ("板块构造", "什么是板块构造？"),
    ("板块构造", "为什么会有地震？"),
    ("板块构造", "大陆是漂移的吗？"),
    ("季风", "什么是季风？"),
    ("季风", "为什么夏天刮东南风？"),
    ("季风", "为什么冬天刮西北风？"),
    ("四季成因", "为什么会有春夏秋冬？"),
    ("四季成因", "四季是怎么形成的？"),
    ("四季成因", "为什么南北半球季节相反？"),
    ("白天黑夜", "为什么会有白天和黑夜？"),
    ("白天黑夜", "昼夜是怎么交替的？"),
    ("白天黑夜", "为什么世界各地时间不同？"),
    ("天文学", "什么是天文学？"),
    ("天文学", "地球绕太阳转吗？"),
    ("天文学", "地心说是什么？"),
    ("夏天冬天", "为什么夏天热冬天冷？"),
    ("夏天冬天", "夏天和地球距离有关吗？"),
    ("夏天冬天", "为什么夏天白天长？"),
    ("光速", "光速是多少？"),
    ("光速", "光速是速度极限吗？"),
    ("光速", "光年是什么？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c4-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:36].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
