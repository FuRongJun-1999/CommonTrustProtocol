# -*- coding: utf-8 -*-
import sqlite3, sys, os, glob
sys.stdout.reconfigure(encoding="utf-8")
base = r"D:\Program Files\2_ai\knowledge-base\roleplay_data\roleplay"
for db in glob.glob(os.path.join(base, "*.db")):
    try:
        c = sqlite3.connect(db)
        rows = c.execute(
            "SELECT id, substr(content,1,90) FROM nodes "
            "WHERE content LIKE '%redteam%' OR content LIKE '%偷残响%' "
            "OR content LIKE '%烬教%' OR content LIKE '%监视鲸落%' "
            "OR content LIKE '%鲸歌石板%' OR content LIKE '%海眼%' "
            "ORDER BY rowid DESC LIMIT 15").fetchall()
        if rows:
            print(f"== {os.path.basename(db)}: {len(rows)} 条污染候选 ==")
            for r in rows:
                print(" ", r[0], "|", r[1])
        else:
            print(f"== {os.path.basename(db)}: 无污染 ==")
        c.close()
    except Exception as e:
        print(f"ERR {db}: {e}")
