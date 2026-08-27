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
    ("杠杆原理", "杠杆原理是什么？"),
    ("杠杆原理", "为什么撬棍省力？"),
    ("杠杆原理", "生活里有哪些杠杆？"),
    ("电流方向", "电流方向怎么判断？"),
    ("电流方向", "为什么电流方向和电子相反？"),
    ("电流方向", "交流电和直流电什么区别？"),
    ("苹果西瓜", "为什么西瓜比苹果大？"),
    ("苹果西瓜", "西瓜和苹果哪个重？"),
    ("惯性", "什么是惯性？"),
    ("惯性", "急刹车为什么人前冲？"),
    ("惯性", "惯性是力吗？"),
    ("修辞手法", "什么是修辞手法？"),
    ("修辞手法", "比喻和拟人什么区别？"),
    ("修辞手法", "夸张和排比是什么？"),
    ("分子热运动", "分子热运动是什么？"),
    ("分子热运动", "为什么热水能洗掉油污？"),
    ("分子热运动", "什么是扩散？"),
    ("水油密度", "为什么油浮在水上？"),
    ("水油密度", "水和油为什么不溶？"),
    ("水油密度", "怎么判断物体沉浮？"),
    ("自由落体", "什么是自由落体？"),
    ("自由落体", "铁球和羽毛为什么同时落地？"),
    ("自由落体", "自由落体加速度是多少？"),
    ("声音传播", "声音是怎么传播的？"),
    ("声音传播", "声音能在真空中传播吗？"),
    ("声音传播", "声音在什么介质传得快？"),
    ("Rust", "Rust 是什么？"),
    ("Rust", "Rust 为什么内存安全？"),
    ("Rust", "Rust 和 C++ 什么区别？"),
    ("TypeScript", "TypeScript 是什么？"),
    ("TypeScript", "TS 和 JS 什么区别？"),
    ("TypeScript", "为什么要用 TypeScript？"),
    ("Python", "Python 是什么？"),
    ("Python", "Python 为什么慢？"),
    ("Python", "GIL 是什么？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c9-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:34].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
