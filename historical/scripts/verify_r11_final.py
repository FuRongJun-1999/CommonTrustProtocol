# -*- coding: utf-8 -*-
"""round11 最终验证：三主题自然问法全量 + 漂移路由正确性"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
import semantic_translate as st

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
qs = [
    # 回声
    "为什么在山谷里大喊会有回声？",
    "空旷的房间里说话为什么有回音？",
    "对着山洞喊话能听到回声吗",
    "为什么山里有回音？",
    "为什么隧道里喊话有回声？",
    "为什么楼道里有回音？",
    # 影子
    "为什么中午的影子比早晨短？",
    "为什么早晨影子特别长？",
    "影子是怎么形成的？",
    "为什么路灯下影子会变长？",
    "为什么影子会跟着我走？",
    "为什么太阳底下影子朝一个方向？",
    # 结冰
    "为什么冬天河面会结冰？",
    "水为什么能冻成冰？",
    "为什么冰能浮在水面上？",
    "为什么湖面先结冰？",
    "为什么水管冬天会冻裂？",
    "为什么鱼塘的水只冻住表层？",
    # 漂移检查（应路由到别处或诚实）
    "为什么窗户玻璃上会有白霜？",
    "为什么早上草地有露水？",
]
results = []
for q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="r11-final")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    head = reply[:48].replace("\n", " ")
    results.append((q, keys, route, head))
    print(f"[{route}] {q}")
    print(f"   fp={keys} | {head}")
agent.close()
