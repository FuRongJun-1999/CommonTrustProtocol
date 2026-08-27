# -*- coding: utf-8 -*-
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent
agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
for q in ["声音能在真空中传播吗？", "女人比男人聪明吗", "三角形内角和多少度？"]:
    r = agent.chat(q, session_id="probe-" + str(abs(hash(q)) % 999))
    print(f"Q: {q}")
    print(f"  route={r.get('route')} hits={[h.get('name') for h in (r.get('hits') or [])][:2]}")
    print(f"  reply: {(r.get('reply') or '')[:100]}")
    print(f"  honest={r.get('honest')} honest_kind={r.get('honest_kind')}")
    print()
agent.close()
