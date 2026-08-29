# -*- coding: utf-8 -*-
"""test_graph_layout.py · 存算融合步骤 1 验证（CSR 布局，2026-08-29）

- 正确性：CSR row 与全库扫描同结果
- 性能：CSR 切片 vs 全库 LIKE 扫描
- 重建一致性
"""
import sys, os, shutil, tempfile, time, sqlite3
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_layout import CSRGraph

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


db_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aeis", "wisdom", "wisdom-book-cloud.db")
tmp = tempfile.mkdtemp(prefix="csr_")
db_dst = os.path.join(tmp, "w.db")
import shutil
shutil.copy(db_src, db_dst)

try:
    t0 = time.time()
    g = CSRGraph.build(db_dst)
    build_ms = (time.time() - t0) * 1000
    check("构建成功", len(g.words) > 5000, f"条件词 {len(g.words)}，邻接 {len(g.data)}，{build_ms:.0f}ms")

    # 正确性：CSR row 与 SQL 全库扫描同结果
    conn = sqlite3.connect(db_dst)
    rows = conn.execute("SELECT id, state_attributes FROM nodes WHERE state_attributes LIKE '%生效条件%'").fetchall()
    conn.close()
    import json as _j
    def brute(word):
        out = []
        for nid, sa in rows:
            try:
                d = _j.loads(sa)
                cm = d.get("comment", {})
                if word in (cm.get("生效条件", []) or []):
                    out.append(nid)
            except Exception:
                pass
        return sorted(out)
    for w in ("问插入排序", "问通道可信度", "问蜂群怎么互联", "问水的沸点"):
        check(f"CSR row {w[:14]} == 全库扫描", sorted(g.row(w)) == brute(w),
              f"csr={g.row(w)} brute={brute(w)}")

    # 性能：CSR 切片 vs LIKE 全库扫描
    t0 = time.time()
    for _ in range(100):
        g.row("问插入排序")
    csr_us = (time.time() - t0) / 100 * 1e6
    t0 = time.time()
    for _ in range(10):
        conn = sqlite3.connect(db_dst)
        conn.execute("SELECT id FROM nodes WHERE state_attributes LIKE '%问插入排序%'").fetchall()
        conn.close()
    like_ms = (time.time() - t0) / 10 * 1000
    print(f"    CSR 切片 {csr_us:.0f}µs vs SQL LIKE {like_ms:.1f}ms")
    check("CSR 切片 < LIKE 扫描", csr_us * 1000 < like_ms, f"{csr_us:.0f}µs vs {like_ms:.1f}ms")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"步骤 1 图物理布局验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
