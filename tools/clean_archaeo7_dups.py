# -*- coding: utf-8 -*-
"""清理批次7 重复卡：每概念保留最新一条（按 content 前缀分组）。"""
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
db = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"
c = sqlite3.connect(db)
rows = c.execute("SELECT id, substr(content,1,8) AS pre FROM nodes WHERE tags LIKE '%archaeo7%' ORDER BY pre, rowid DESC").fetchall()
seen = set()
deleted = 0
for nid, pre in rows:
    if pre in seen:
        c.execute("DELETE FROM nodes WHERE id=?", (nid,))
        deleted += 1
    else:
        seen.add(pre)
c.commit()
left = c.execute("SELECT COUNT(*) FROM nodes WHERE tags LIKE '%archaeo7%'").fetchone()[0]
print(f"删除重复 {deleted} 条，剩余 {left} 条（应 13 概念各 1）")
# 复查分组
rows2 = c.execute("SELECT substr(content,1,8), COUNT(*) FROM nodes WHERE tags LIKE '%archaeo7%' GROUP BY 1").fetchall()
for r in rows2:
    print(f"  {r[0]}: {r[1]}")
c.close()
