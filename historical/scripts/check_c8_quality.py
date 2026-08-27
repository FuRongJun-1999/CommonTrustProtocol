# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["防晒穿什么颜色？", "冬天穿什么颜色暖和？", "饭后散步好不好？", "每天散步好吗？", "散步能减肥吗？"]:
    r = agent.chat(q, session_id="c8-q")
    print("Q:", q, "| route:", r.get("route"))
    print("   ", r.get("reply", "")[:70].replace("\n", " "))
agent.close()
