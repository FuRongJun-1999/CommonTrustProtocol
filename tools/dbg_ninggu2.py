# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
import semantic_translate as st
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
q = "凝固是熔化的逆过程吗？"
fp = st.encode(q)
print("fp:", [k for k in fp if k in st.REVERSE_DAILY])
r = agent.chat(q, session_id="dbg-ng")
print("route:", r.get("route"))
print("reply:", r.get("reply", "")[:60].replace("\n", " "))
agent.close()
