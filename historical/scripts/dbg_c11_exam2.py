# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
from aeis.api import Agent
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
# 直接调 chat_engine 看 emotion
from wisdom import chat_engine as ce
msg = "考试紧张怎么办？"
emotion = ce._detect_emotion_semantic(msg)
print("emotion:", emotion)
r = agent.chat(msg, session_id="dbg-exam2")
print("reply:", r.get("reply", "")[:120].replace("\n", " "))
# 模拟 fp 块
fp = st.encode(msg)
_long = [t for t in fp if len(t) >= 2 and t in st.REVERSE_DAILY]
print("_long:", _long)
agent.close()
