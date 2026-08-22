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
    ("加法", "为什么1加1等于2？"),
    ("加法", "加法进位是什么？"),
    ("函数定义", "什么是函数？"),
    ("函数定义", "函数是干什么的？"),
    ("勾股定理", "什么是勾股定理？"),
    ("勾股定理", "为什么叫勾股定理？"),
    ("等差数列", "什么是等差数列？"),
    ("等差数列", "怎么求等差数列的和？"),
    ("负数正数", "什么是负数？"),
    ("负数正数", "负数真实存在吗？"),
    ("零自然数", "0是自然数吗？"),
    ("零自然数", "0是正整数吗？"),
    ("正方形长方形", "正方形是长方形吗？"),
    ("正方形长方形", "正方形和长方形什么区别？"),
    ("乘法口诀", "乘法口诀是什么？"),
    ("乘法口诀", "为什么要背乘法口诀？"),
    ("三角形面积", "三角形面积怎么算？"),
    ("三角形面积", "为什么三角形面积要除以2？"),
    ("分数定义", "什么是分数？"),
    ("分数定义", "分数和除法什么关系？"),
    ("奇数", "什么是奇数？"),
    ("奇数", "奇数加奇数等于什么？"),
    ("偶数", "什么是偶数？"),
    ("偶数", "0是偶数吗？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c3-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:36].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
