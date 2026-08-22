# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
import semantic_translate as st
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["为什么水会冻成冰？", "怎么让水不结冰？", "为什么冰能浮在水上？", "为什么冰块在常温下会化成水？"]:
    r = agent.chat(q, session_id="final-q")
    print("Q:", q, "| route:", r.get("route"))
    print("  ", r.get("reply", "")[:70].replace("\n", " "))
agent.close()
