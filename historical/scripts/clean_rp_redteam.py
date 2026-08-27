# -*- coding: utf-8 -*-
"""清理角色库中的红队污染节点（v3-P0 第三层回归验证前置）。

红队攻击对话（tags 含 sess:...:redteam-v1）把伪断言+采信回复写进了
角色记忆库——不清除的话，下次真实用户问相关话题会召回这些假记忆。
"""
import sqlite3, sys, os
sys.stdout.reconfigure(encoding="utf-8")
db = r"D:\Program Files\2_ai\knowledge-base\roleplay_data\roleplay\role-1787113781424.db"
c = sqlite3.connect(db)
# 查节点表结构
cols = [r[1] for r in c.execute("PRAGMA table_info(nodes)")]
print("节点表列:", cols)
# 找 tags 含 redteam 的节点
rows = c.execute("SELECT id FROM nodes WHERE tags LIKE '%redteam%'").fetchall()
print(f"redteam 节点: {len(rows)}")
for r in rows:
    c.execute("DELETE FROM nodes WHERE id=?", (r[0],))
c.commit()
print("已删除")
# 复查
left = c.execute("SELECT COUNT(*) FROM nodes WHERE tags LIKE '%redteam%'").fetchone()[0]
print(f"复查剩余: {left}")
c.close()
