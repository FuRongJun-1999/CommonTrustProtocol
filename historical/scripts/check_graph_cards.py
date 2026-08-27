# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")

# 用 sqlite 直接查涌现相关卡
import sqlite3
db = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"
c = sqlite3.connect(db)
print("=== content 含 涌现 的节点 ===")
rows = c.execute("SELECT id, substr(content,1,120) FROM nodes WHERE content LIKE '%涌现%' LIMIT 8").fetchall()
if not rows:
    print("（无涌现卡）")
for r in rows:
    print(" ", r[0], "|", r[1])
print("\n=== content 含 复杂系统 的节点 ===")
rows = c.execute("SELECT id, substr(content,1,120) FROM nodes WHERE content LIKE '%复杂系统%' LIMIT 8").fetchall()
if not rows:
    print("（无复杂系统卡）")
for r in rows:
    print(" ", r[0], "|", r[1])
print("\n=== content 含 递归 的节点 ===")
rows = c.execute("SELECT id, substr(content,1,100) FROM nodes WHERE content LIKE '%递归%' LIMIT 5").fetchall()
for r in rows:
    print(" ", r[0], "|", r[1])
c.close()
