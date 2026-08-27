# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["考试紧张怎么办？"]:
    r = agent.chat(q, session_id="dbg-exam")
    print("Q:", q, "| route:", r.get("route"))
    print("   full reply:", r.get("reply", "")[:150].replace("\n", " "))
agent.close()
