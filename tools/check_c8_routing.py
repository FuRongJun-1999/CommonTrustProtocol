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
    ("冰箱保鲜", "为什么食物放冰箱不容易坏？"),
    ("冰箱保鲜", "冰箱能杀菌吗？"),
    ("冰箱保鲜", "冷藏和冷冻什么区别？"),
    ("热水洗澡", "为什么洗澡用热水舒服？"),
    ("热水洗澡", "洗澡水多热合适？"),
    ("热水洗澡", "热水澡洗太久好吗？"),
    ("浅色衣服", "为什么夏天穿浅色衣服凉快？"),
    ("浅色衣服", "防晒穿什么颜色？"),
    ("浅色衣服", "冬天穿什么颜色暖和？"),
    ("远眺护眼", "为什么要远眺护眼？"),
    ("远眺护眼", "远眺能防近视吗？"),
    ("远眺护眼", "眼疲劳怎么缓解？"),
    ("饭后运动", "为什么饭后不能马上运动？"),
    ("饭后运动", "饭后多久能运动？"),
    ("饭后运动", "饭后散步好不好？"),
    ("散步", "散步有什么好处？"),
    ("散步", "每天散步好吗？"),
    ("散步", "散步能减肥吗？"),
    ("微波炉", "微波炉是怎么加热的？"),
    ("微波炉", "微波炉为什么不能放金属？"),
    ("微波炉", "微波炉加热有害吗？"),
    ("光合产物", "光合作用产生了什么？"),
    ("光合产物", "氧气是光合产生的吗？"),
    ("光合产物", "光合产物和呼吸产物什么区别？"),
    ("数组", "什么是数组？"),
    ("数组", "数组下标为什么从0开始？"),
    ("数组", "数组和列表什么区别？"),
    ("调试", "什么是调试？"),
    ("调试", "bug有哪些类型？"),
    ("调试", "怎么定位bug？"),
    ("编程类", "什么是编程里的类？"),
    ("编程类", "类和对象什么区别？"),
    ("编程变量", "什么是编程里的变量？"),
    ("编程变量", "变量为什么叫变量？"),
    ("编程函数", "什么是编程里的函数？"),
    ("编程函数", "函数的参数是什么？"),
    ("编程循环", "什么是编程里的循环？"),
    ("编程循环", "while循环怎么用？"),
    ("编程循环", "循环为什么要小心？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c8-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:34].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
