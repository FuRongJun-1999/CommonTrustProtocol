# -*- coding: utf-8 -*-
"""第3步：结构重要性重算 lingshu_importance_recalc（v2.1 首版）
只升不降（importance 为地板）；加性提升；BOOST_CAP 限制单次涨幅。
用法: python importance_recalc_v2.py --dry   # 只报告不动数据
      python importance_recalc_v2.py --apply # 应用
"""
import sys, io, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from aeis.core import SpacetimeMemoryEngine

DB = r'C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db'
BETA, GAMMA, C, BOOST_CAP = 0.30, 0.40, 6.0, 0.15

ap = argparse.ArgumentParser()
ap.add_argument('--apply', action='store_true', help='应用更新（默认干跑）')
ap.add_argument('--top', type=int, default=30)
args = ap.parse_args()

eng = SpacetimeMemoryEngine(db_path=DB, identity="importance_recalc_v2.1")
store = eng.store
store.conn.execute("PRAGMA busy_timeout=8000")

# 边统计
c = store.conn.cursor()
c.execute("SELECT source_id, target_id, relation_type FROM edges")
edges = c.fetchall()
causal_out = {}
deg = {}
for s, t, rt in edges:
    deg[s] = deg.get(s, 0) + 1
    deg[t] = deg.get(t, 0) + 1
    if rt == 'causal':
        causal_out[s] = causal_out.get(s, 0) + 1
max_deg = max(deg.values()) if deg else 1

# 全节点
c.execute("SELECT id, importance, layer, access_count FROM nodes")
nodes = c.fetchall()
movers = []
for nid, imp, layer, acc in nodes:
    if imp is None or imp >= 0.95:
        continue
    d = deg.get(nid, 0)
    co = causal_out.get(nid, 0)
    if d < 5 and co < 3:
        continue  # 无结构数据不动（地板语义）
    ci = min(co, C) / C
    conn = d / max_deg
    boost = BETA * ci + GAMMA * conn
    boost = min(boost, BOOST_CAP)
    new_imp = min(1.0, imp + boost)
    if new_imp - imp >= 0.02:
        movers.append((nid, imp, new_imp, d, co, layer, acc))

movers.sort(key=lambda x: (x[2] - x[1]), reverse=True)
print(f'候选提升节点: {len(movers)}（max_deg={max_deg}）\n')
print(f'{"新-旧":>6} {"旧":>5} {"新":>5} {"度":>4} {"因":>3} {"访问":>6}  节点')
for nid, imp, new_imp, d, co, layer, acc in movers[:args.top]:
    print(f'{new_imp-imp:+.3f} {imp:.3f} {new_imp:.3f} {d:>4} {co:>3} {acc:>6}  {nid[:40]}')

if args.apply:
    applied = 0
    for nid, imp, new_imp, d, co, layer, acc in movers:
        store.update_node_importance(nid, round(new_imp - imp, 4))
        applied += 1
    print(f'\n[APPLIED] 已更新 {applied} 个节点')
else:
    print('\n[dry-run] 未写库。加 --apply 应用。')
