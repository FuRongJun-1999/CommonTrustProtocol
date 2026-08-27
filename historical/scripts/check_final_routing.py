# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
qs = [
    ("沸腾", "为什么水烧开会咕嘟咕嘟冒泡？"),
    ("沸腾", "为什么水到100°C就开？"),
    ("沸腾", "为什么高原上水煮不熟饭？"),
    ("沸腾", "为什么烧水会有声音？"),
    ("液化", "为什么哈气在镜子上会变成小水珠？"),
    ("液化", "冬天眼镜进屋为什么起雾？"),
    ("液化", "露水是怎么来的？"),
    ("液化", "怎么让眼镜不起雾？"),
    ("凝固", "为什么水会冻成冰？"),
    ("凝固", "凝固和结冰一样吗？"),
    ("凝固", "为什么冰能浮在水上？"),
    ("凝固", "怎么让水不结冰？"),
    ("熔化", "为什么冰块在常温下会化成水？"),
    ("熔化", "熔化和融化一样吗？"),
    ("熔化", "怎么让冰化得快？"),
    ("熔化", "冰水混合为什么还是0°C？"),
    ("升华", "为什么樟脑丸放衣柜里会变小？"),
    ("升华", "干冰为什么会冒白烟？"),
    ("升华", "升华是吸热还是放热？"),
    ("凝华", "为什么冬天窗户上会有霜花？"),
    ("凝华", "霜是怎么形成的？"),
    ("凝华", "雪是怎么形成的？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="final-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:40].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
