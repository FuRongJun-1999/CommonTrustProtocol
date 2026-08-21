# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
c = sqlite3.connect(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
n = c.execute("SELECT COUNT(*) FROM nodes WHERE tags LIKE '%archaeo7%'").fetchone()[0]
print("archaeo7 标签卡数:", n)
# 按内容前缀统计重复
rows = c.execute("SELECT substr(content,1,8) AS pre, COUNT(*) FROM nodes WHERE tags LIKE '%archaeo7%' GROUP BY pre").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]}")
# 全部考古卡
n2 = c.execute("SELECT COUNT(*) FROM nodes WHERE tags LIKE '%archaeo%'").fetchone()[0]
print("全部考古标签卡:", n2)
c.close()
