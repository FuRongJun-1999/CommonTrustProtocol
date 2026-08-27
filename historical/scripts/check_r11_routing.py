# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
import semantic_translate as st

qs = [
    "为什么冬天河面会结冰？",
    "水为什么能冻成冰？",
    "为什么水会结冰？",
    "为什么冰能浮在水面上？",
    "为什么湖面会结冰？",
    "水面结冰是什么原理？",
    "为什么中午的影子比早晨短？",
    "影子是怎么形成的？",
    "为什么路灯下影子会变长？",
    "为什么在山谷里大喊会有回声？",
    "空旷的房间里说话为什么有回音？",
    "为什么对着山洞喊话能听到回声？",
]
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="r11-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    print("Q:", q)
    print("  fp keys:", keys)
    print("  route:", route, "| reply head:", reply[:60].replace("\n", " "))
agent.close()
