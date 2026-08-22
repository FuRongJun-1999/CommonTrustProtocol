# -*- coding: utf-8 -*-
import sys, os, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
importlib.reload(st)
print("惯性 triggers:", st.DOMAIN_SYNONYM_CLUSTERS.get("惯性"))
from aeis.api import Agent
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["急刹车为什么人前冲？", "惯性是力吗？"]:
    r = agent.chat(q, session_id="dbg-inertia")
    print("Q:", q, "| route:", r.get("route"))
    print("   ", r.get("reply", "")[:60].replace("\n", " "))
agent.close()
