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
    ("刷牙护牙", "为什么要刷牙？"),
    ("刷牙护牙", "怎么刷牙才正确？"),
    ("刷牙护牙", "横着刷为什么不好？"),
    ("早睡早起", "为什么要早睡早起？"),
    ("早睡早起", "熬夜有什么坏处？"),
    ("早睡早起", "怎么做到早睡早起？"),
    ("煮饭原理", "为什么煮饭饭会熟？"),
    ("煮饭原理", "煮饭水放多少合适？"),
    ("开水烫", "被开水烫了怎么办？"),
    ("开水烫", "烫伤能涂牙膏酱油吗？"),
    ("晒太阳补钙", "为什么晒太阳能补钙？"),
    ("晒太阳补钙", "隔着玻璃晒太阳有用吗？"),
    ("开窗通风", "为什么要开窗通风？"),
    ("开窗通风", "多久通一次风？"),
    ("运动热身", "为什么要运动前热身？"),
    ("运动热身", "热身多久合适？"),
    ("运动拉伸", "为什么要运动后拉伸？"),
    ("运动拉伸", "热身和拉伸什么区别？"),
    ("走路锻炼", "走路能锻炼身体吗？"),
    ("走路锻炼", "每天走多少步？"),
    ("久坐活动", "为什么要少久坐？"),
    ("久坐活动", "多久起身一次？"),
    ("用眼休息", "为什么用眼久了要休息？"),
    ("用眼休息", "20-20-20法则是什么？"),
    ("吹干头发", "为什么要吹干头发？"),
    ("吹干头发", "湿发睡觉有什么坏处？"),
    ("热水解冻", "为什么热水解冻不好？"),
    ("热水解冻", "怎么解冻最安全？"),
    ("保暖防感冒", "为什么天冷要保暖？"),
    ("保暖防感冒", "保暖怎么防感冒？"),
    ("睡前不玩", "为什么睡前不玩手机？"),
    ("睡前不玩", "褪黑素是什么？"),
    ("喝水止渴", "为什么渴了要喝水？"),
    ("喝水止渴", "每天喝多少水？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c10-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:32].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
