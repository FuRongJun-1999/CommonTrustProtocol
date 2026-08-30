# -*- coding: utf-8 -*-
"""merge_lingshu_dbs.py · 双库合并（T4 后统一记忆库 · 2026-08-30 荣决策方案 B）

主库（aeis_memory.db，大脑权威线 4K 节点）+ 源库（dsh profile lingshu.db，
身体/对话线 57K 节点）→ 合并库（新文件，不动任何在线库）。
策略：ATTACH 源库 + INSERT OR IGNORE（id 主键去重，主库优先）。
不迁：action_logs（审计历史留在各自库）/engine_meta（实例元数据）。
"""
import sys, os, shutil, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

MAIN_DB = r"D:\Program Files\2_ai\AEIS\data\aeis_memory.db"
SRC_DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
OUT_DB = r"D:\Program Files\2_ai\AEIS\data\aeis_memory_merged.db"
BACKUP_DIR = r"D:\Program Files\2_ai\AEIS\data\merge_backup_20260830"
TABLES = ["nodes", "edges", "entities", "skills", "protections",
          "blindspots", "rejected_paths", "promotion_proposals", "verifier_standards"]

os.makedirs(BACKUP_DIR, exist_ok=True)
# 1. 备份两库
shutil.copy2(MAIN_DB, os.path.join(BACKUP_DIR, "aeis_memory.db.bak"))
shutil.copy2(SRC_DB, os.path.join(BACKUP_DIR, "lingshu_profile.db.bak"))
print("备份完成 →", BACKUP_DIR)

# 2. 合并库 = 主库副本（在线库不动）
if os.path.exists(OUT_DB):
    os.unlink(OUT_DB)
shutil.copy2(MAIN_DB, OUT_DB)

conn = sqlite3.connect(OUT_DB)
conn.execute("ATTACH DATABASE ? AS src", (SRC_DB,))
before = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
print(f"合并前主库 nodes: {before}")

# 3. 逐表 INSERT OR IGNORE（列结构同构已验证）
for t in TABLES:
    try:
        src_cols = [r[1] for r in conn.execute(f"PRAGMA src.table_info({t})").fetchall()]
        dst_cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})").fetchall()]
        if not src_cols or not dst_cols:
            print(f"  跳过 {t}（表缺失）")
            continue
        common = [c for c in dst_cols if c in src_cols]
        collist = ",".join(common)
        cur = conn.execute(
            f"INSERT OR IGNORE INTO main.{t} ({collist}) "
            f"SELECT {collist} FROM src.{t}")
        print(f"  {t}: +{cur.rowcount}")
    except Exception as e:
        print(f"  {t}: 失败 {e}")
conn.commit()

after = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
conn.close()
print(f"合并后: nodes={after}（+{after-before}）edges={edges}")
print(f"合并库: {OUT_DB}")
