# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
import semantic_translate as st
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["为什么高原上水煮不熟饭？", "为什么海拔高的地方水烧不开？", "为什么高压锅熟得快？",
          "为什么潜水越深压力越大？", "用吸管能把饮料吸上来吗？"]:
    r = agent.chat(q, session_id="guard-test")
    print("Q:", q, "| route:", r.get("route"))
    print("   ", r.get("reply", "")[:60].replace("\n", " "))
agent.close()
