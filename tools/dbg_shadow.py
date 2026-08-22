# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
from aeis.api import Agent

# 检查光的直线传播簇是否含 影子
cl = st.DOMAIN_SYNONYM_CLUSTERS.get("光的直线传播", [])
print("光的直线传播 cluster:", cl)
cl2 = st.SYNONYM_CLUSTERS.get("光的直线传播", [])
print("SYNONYM cluster:", cl2)
print("REVERSE has 光的直线传播:", "光的直线传播" in st.REVERSE_DAILY)

q = "为什么中午的影子比早晨短？"
fp = st.encode(q)
print("fp:", fp)
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
r = agent.chat(q, session_id="dbg-shadow")
print("route:", r.get("route"))
print("reply head:", r.get("reply", "")[:80].replace("\n", " "))
agent.close()
