# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
db = r"D:\Program Files\2_ai\knowledge-base\roleplay_data\roleplay\role-1787113781424.db"
c = sqlite3.connect(db)
# 精确匹配 json 标签数组中的 "plot"
rows = c.execute("SELECT id, substr(content,1,110), importance, tags FROM nodes WHERE tags LIKE '%\"plot\"%' ORDER BY importance DESC LIMIT 10").fetchall()
print(f"tags 含 \"plot\" 的节点: {len(rows)}")
for r in rows:
    print(f"  imp={r[2]} | {r[1]}")
    print(f"      tags={r[3]}")
# 也看看 no_forget 的
print("\n=== 含 no_forget / protected 的节点 ===")
rows2 = c.execute("SELECT id, substr(content,1,90), importance, tags FROM nodes WHERE tags LIKE '%no_forget%' ORDER BY importance DESC LIMIT 5").fetchall()
for r in rows2:
    print(f"  imp={r[2]} | {r[1]} | tags={r[3]}")
c.close()
