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
    ("降落伞", "为什么跳伞能安全落地？"),
    ("降落伞", "降落伞为什么能让降落变慢？"),
    ("降落伞", "没有降落伞怎么掉都摔死吗？"),
    ("降落伞", "为什么小鸟从树上掉下来摔不死？"),
    ("秋千", "为什么秋千越荡越高？"),
    ("秋千", "秋千为什么能一直荡？"),
    ("秋千", "为什么秋千越来越低最后停下？"),
    ("秋千", "钟摆和秋千一样吗？"),
    ("反射", "为什么镜子能照出自己？"),
    ("反射", "镜子里的字为什么是反的？"),
    ("反射", "镜子里的是真人吗？"),
    ("反射", "倒影和镜子一样吗？"),
    ("蒸发", "为什么湿衣服晾着会干？"),
    ("蒸发", "水洒地上为什么过会儿就不见了？"),
    ("蒸发", "为什么风大衣服干得快？"),
    ("蒸发", "为什么把衣服摊开干得快？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="r15-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:44].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
