# -*- coding: utf-8 -*-
"""抽查「知识卡源重建」宽泛卡：对卡名提问看能否 self 直答。

目标：找出「卡在图谱但无 direct_answer → llm 兜底」的卡，
这些是白箱的静默盲区（卡在但答不出）。
"""
import sqlite3, sys, os
sys.stdout.reconfigure(encoding="utf-8")
c = sqlite3.connect(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
rows = c.execute("SELECT state_attributes FROM nodes WHERE content LIKE '%知识卡源重建%' LIMIT 80").fetchall()
names = set()
for (sa,) in rows:
    try:
        import json
        d = json.loads(sa or "{}")
        nm = d.get("name")
        if nm:
            names.add(nm)
    except Exception:
        pass
c.close()
print(f"知识卡源重建卡名: {len(names)} 张")
print(sorted(names)[:50])
