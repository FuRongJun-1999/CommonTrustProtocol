# -*- coding: utf-8 -*-
"""LLM 自然问法迁移测试：拖延主题 12 问 → agent.chat 完整路由"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

VARIANTS = [
    "明明想做事就是拖到最后一刻，到底怎么才能开始第一下？",
    "事情一大起来脑子就空白，是不是我太没用了？",
    "我只要坐下一会儿就能进入状态，到底该怎么逼自己开始？",
    "干点小事没感觉，一碰大项目就怂，怎么办？",
    "为什么一到要交报告的时候特别慌？",
    "孩子写作业磨蹭半天不肯动笔，我该怎么办？",
    "想减肥想健身就是想不起来行动，是不是没目标？",
    "一看到任务清单就头疼，根本不知道从哪下手。",
    "老板催得紧了我还是不动手，到底卡在哪了？",
    "每次都说明天再做，结果越拖越焦虑，怎么破？",
    "我就是静不下来，稍微一复杂就想逃避，咋整？",
    "大任务拆成小块好像能行，可我不知道怎么拆啊。",
]

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
PROC_HINTS = ["拖延", "启动", "拆小", "5分钟", "先开始", "任务", "行动", "焦虑", "开始", "小目标", "借口"]
print("=== LLM 自然问法迁移（拖延）===")
hits = 0
for i, q in enumerate(VARIANTS, 1):
    r = agent.chat(q, session_id=f"nat-{i}")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    is_proc = route == "self" and any(h in reply for h in PROC_HINTS)
    if is_proc:
        hits += 1
    print(f"[{'✓' if is_proc else '✗'}] ({route}) {q[:24]} | {reply[:42]}")
print(f"\n=== 白箱实际命中: {hits}/{len(VARIANTS)} ===")
agent.close()
