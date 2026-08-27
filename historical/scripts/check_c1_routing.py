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
    ("摩擦", "为什么搓手会发热？"),
    ("摩擦", "鞋底为什么有花纹？"),
    ("电流", "电流是什么？"),
    ("电流", "为什么通电灯才亮？"),
    ("浮力", "为什么木头能漂在水上？"),
    ("浮力", "为什么铁船能浮在水上？"),
    ("重力", "为什么苹果熟了会往下掉？"),
    ("重力", "为什么在太空会飘起来？"),
    ("杠杆", "为什么撬棍能省力？"),
    ("杠杆", "生活里有哪些杠杆？"),
    ("大气压", "为什么吸管能把饮料吸上来？"),
    ("大气压", "拔火罐为什么能吸住皮肤？"),
    ("电压", "电压是什么？"),
    ("电压", "为什么家庭电会电人？"),
    ("折射", "为什么筷子插水里看起来弯了？"),
    ("折射", "为什么游泳池底看起来浅？"),
    ("光的直线传播", "为什么影子是黑黑的？"),
    ("光的直线传播", "小孔成像为什么是倒的？"),
    ("电磁感应", "发电机为什么能发电？"),
    ("电磁感应", "电磁感应是什么？"),
    ("滑轮", "为什么旗杆顶上有轮子？"),
    ("滑轮", "定滑轮和动滑轮什么区别？"),
    ("风化", "为什么石头会碎？"),
    ("风化", "为什么山会被磨平？"),
    ("潮汐", "为什么海水每天定时涨落？"),
    ("潮汐", "潮汐是怎么形成的？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c1-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:40].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
