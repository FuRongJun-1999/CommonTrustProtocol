# -*- coding: utf-8 -*-
"""v2.2 因果上游度传播回归测试：越上游影响越大，越要记录"""
import sys, io, os, tempfile, time, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from aeis.core import SpacetimeMemoryEngine

tmp = os.path.join(tempfile.gettempdir(), f"infl_{int(time.time())}.db")
eng = SpacetimeMemoryEngine(db_path=tmp, identity="t")
st = eng.store
c = st.conn.cursor()
now = time.time()
cs = json.dumps({"observation_position":"测试","observation_tool":"sql","time_window":[now,now+3600],"existence_constraint":"测试"})
COLS = "id,content,modality,spatial_coordinates,temporal_coordinate,condition_space,importance,confidence,layer,access_count,last_access,created_at,tags,semantic_coordinates,state_attributes,entity_id"
def ins(nid, imp):
    c.execute(f"INSERT INTO nodes ({COLS}) VALUES ({','.join('?'*16)})",
              (nid, f"节点{nid}", "text", "{}", now, cs, imp, 0.5, "knowledge", 0, now, now, "[]", "{}", "{}", None))
def edge(s, t, rt, cf):
    c.execute("INSERT INTO edges (id,source_id,target_id,relation_type,confidence,verified,created_at) VALUES (?,?,?,?,?,1,?)",
              (f"e_{s}_{t}", s, t, rt, cf, now))
# 因果链 A -> B -> C（置信度 0.9 / 0.8），分支 A -> D（0.7）
ins("A", 0.5); ins("B", 0.8); ins("C", 0.9); ins("D", 0.6)
edge("A","B","causal",0.9); edge("B","C","causal",0.8); edge("A","D","causal",0.7)
st.conn.commit()

def get(nid):
    c.execute("SELECT importance, state_attributes FROM nodes WHERE id=?", (nid,))
    r = c.fetchone()
    sa = json.loads(r[1]) if r and r[1] else {}
    return r[0], sa.get("concept_influence")

print("== dry_run（不写库） ==")
r = st.recalc_structural_importance(dry_run=True, protect_threshold=1.0, floor_importance=0.9)
print("top_influence:", r["top_influence"])
assert r["mode"]=="dry_run"
impA0, infA0 = get("A")
assert impA0 == 0.5 and not infA0, "dry_run 不应写库"
print("  dry_run 未写库 ✓")

print("== apply（越上游影响越大） ==")
r = st.recalc_structural_importance(dry_run=False, protect_threshold=1.0, floor_importance=0.9)
print("protected:", r["protected"], "influence_nodes:", r["influence_nodes"])
impA, infA = get("A"); impB, infB = get("B"); impC, infC = get("C"); impD, infD = get("D")
print(f"  A: imp={impA} infl={infA}")
print(f"  B: imp={impB} infl={infB}")
print(f"  C: imp={impC} infl={infC}")
print(f"  D: imp={impD} infl={infD}")
assert infA > infB > (infC or 0), "越上游影响越大：A>B>C"
assert (infD or 0) == 0, "叶子节点（无下游）影响力应为 0"
assert infA == 1.464, f"A 期望 0.9*0.8/1+0.9*0.8*0.9/2+0.7*0.6/1=1.464, 实际 {infA}"

print("== 越上游越要记录：保护 + 保底 ==")
prot = set(st.get_protected_nodes())
assert "A" in prot and "B" not in prot, "A 应被结构保护，B 未达阈值"
assert impA == 0.9, f"A importance 保底 0.9, 实际 {impA}"
c.execute("SELECT tags FROM nodes WHERE id='A'")
assert "no_forget" in json.loads(c.fetchone()[0]), "A 应有 no_forget 标记"
print("  A 被保护 + 保底 0.9 + no_forget ✓；B 未达阈值 ✓")

st.conn.close()
for f in (tmp, tmp+"-wal", tmp+"-shm"):
    try: os.remove(f)
    except OSError: pass
print("\nPASS: 因果上游度传播 + 结构保护全部通过")
