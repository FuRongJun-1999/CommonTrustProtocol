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
    ("发烧", "为什么会发烧？"),
    ("发烧", "发烧是坏事吗？"),
    ("发烧", "发烧能捂汗吗？"),
    ("饿", "为什么会饿？"),
    ("饿", "饿过头为什么反而不饿？"),
    ("考试", "考试前怎么复习？"),
    ("考试", "考试紧张怎么办？"),
    ("考试", "考试没考好怎么办？"),
    ("氧气", "氧气是什么？"),
    ("氧气", "人为什么要吸氧气？"),
    ("氧气", "氧气为什么支持燃烧？"),
    ("叶子绿色", "为什么叶子是绿色的？"),
    ("叶子绿色", "叶绿素是什么？"),
    ("叶子绿色", "为什么秋天叶子变黄？"),
    ("飞机汽车", "为什么飞机比汽车快？"),
    ("飞机汽车", "远途选飞机还是高铁？"),
    ("地球公转", "什么是地球公转？"),
    ("地球公转", "公转和自转什么区别？"),
    ("地球公转", "为什么有闰年？"),
    ("信任", "什么是信任？"),
    ("信任", "信任怎么建立？"),
    ("信任", "信任怎么破坏？"),
    ("价值观", "什么是价值观？"),
    ("价值观", "价值观会变吗？"),
    ("价值观", "价值观和道德什么区别？"),
    ("记忆", "什么是记忆？"),
    ("记忆", "怎么提高记忆？"),
    ("记忆", "记忆和睡眠什么关系？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c11-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:32].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
