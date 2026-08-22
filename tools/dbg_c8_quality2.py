# -*- coding: utf-8 -*-
import sys, os, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
importlib.reload(st)
from aeis.api import Agent
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["防晒穿什么颜色？", "散步能减肥吗？"]:
    r = agent.chat(q, session_id="dbg-q2")
    print("Q:", q)
    print("   ", r.get("reply", "")[:80].replace("\n", " "))
agent.close()
