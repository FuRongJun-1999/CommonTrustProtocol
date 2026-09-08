# -*- coding: utf-8 -*-
"""export_ccg_dump.py · 从 sqlite 导出 CCG 注释数据（card_route 路由索引）

一次性导出：aeis/wisdom/wisdom-book-cloud.db → aeis/knowledge/_ccg_dump.json
后续心跳新增知识点时重跑本脚本即可更新路由索引。
"""
import sqlite3, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
OUT = os.path.join(ROOT, "aeis", "knowledge", "_ccg_dump.json")

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""SELECT id, state_attributes, content FROM nodes
               WHERE state_attributes LIKE '%"comment"%'""")
rows = []
for nid, sa_json, content in cur.fetchall():
    rows.append({"id": nid, "sa_json": sa_json, "content": content or ""})
conn.close()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False)

print(f"CCG dump 导出完成: {len(rows)} 条路由记录 → {OUT}")
