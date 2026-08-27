# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
c = sqlite3.connect(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
print("表:", tables)
for t in tables:
    if "edge" in t.lower():
        cols = [r[1] for r in c.execute(f"PRAGMA table_info({t})")]
        print(f"\n{t}: {cols}")
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  行数: {cnt}")
        for r in c.execute(f"SELECT * FROM {t} LIMIT 4"):
            print("  ", [str(x)[:30] for x in r])
c.close()
