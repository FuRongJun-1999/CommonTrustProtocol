# -*- coding: utf-8 -*-
"""test_semantic_anchor_graph · 里程碑1.2 3D语义锚点图单元测试"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from aeis.semantic_anchor_graph import (
    SemanticAnchorGraph, SemanticAnchor, register_relation_type, RELATION_TYPES)

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

g = SemanticAnchorGraph()

# --- 节点：3D 语义锚点 ---
table_id = g.add("桌子", (0, 0.7, 5), size=(1.5, 0.1, 1.0), confidence=0.9,
                 provenance="view1@yaw0")
chair_id = g.add("椅子", (0.8, 0.4, 4.8), confidence=0.8, provenance="view2@yaw30")
cup_id = g.add("杯子", (0.2, 0.8, 5.1), size=(0.08, 0.1, 0.08), confidence=0.7,
               provenance="view1@yaw0")
room_id = g.add("房间", (0, 1.5, 5), size=(8, 3, 8), confidence=0.9)
check("4 anchors added", len(g.anchors) == 4)

# --- 锚点属性（开放扩展）---
a = g.get(table_id)
check("anchor has category/center/conf", a.category == "桌子" and a.confidence == 0.9)
check("anchor provenance", a.provenance == "view1@yaw0")
check("anchor attrs open", a.attrs == {})

# --- 边：关系 ---
g.relate(room_id, table_id, "包含", 0.9)
g.relate(table_id, cup_id, "支撑", 0.8)
g.relate(table_id, chair_id, "相邻", 0.6, attrs={"distance": 0.7})
g.relate(chair_id, table_id, "朝向", 0.5)
check("4 edges", len(g.edges) == 4)

# --- 事物是其关系的总和 ---
rels_table = g.relations_of(table_id)
check("table relations = 4 (in+out)", len(rels_table) == 4, str(len(rels_table)))
cats = sorted(r["relation"] for r in rels_table)
check("table has 包含/支撑/相邻/朝向", sorted(cats) == sorted(["包含", "支撑", "相邻", "朝向"]), str(cats))

# --- 邻居查询（按关系过滤）---
n_cup = g.neighbors(cup_id, relation="支撑")
check("cup neighbor via 支撑", len(n_cup) == 1 and n_cup[0]["id"] == table_id, str(n_cup))

# --- 类别/区域查询 ---
chairs = g.query(category="椅子")
check("query by category", len(chairs) == 1 and chairs[0].category == "椅子")
region = (0, 0, 4, 2, 2, 6)
in_region = g.query(region=region)
check("query by region", len(in_region) >= 3)

# --- 关系推理（空间邻近 → 相邻/支撑）---
g2 = SemanticAnchorGraph()
g2.add("书本", (0, 0.8, 5), size=(0.2, 0.02, 0.15))      # 在桌上
g2.add("桌子", (0, 0.7, 5), size=(1.5, 0.1, 1.0))
g2.add("椅子", (2.5, 0.4, 5))                             # 较远
added = g2.infer_relations(distance_threshold=1.0)
check("infer relations added", added >= 1, str(added))
rels = g2.relations_of(g2.query(category="书本")[0].id)
support_found = any(r["relation"] == "支撑" for r in rels)
check("book supported by table", support_found, str(rels))

# --- 可扩展：注册新关系类型 ---
register_relation_type("发光", dim="visual", desc="A 发光照亮 B")
check("new relation registered", "发光" in RELATION_TYPES)
g3 = SemanticAnchorGraph()
id1 = g3.add("灯", (1, 2, 5))
id2 = g3.add("桌子", (0, 0.7, 5))
g3.relate(id1, id2, "发光", 0.9)
check("custom relation edge", len(g3.edges) == 1 and g3.edges[0].relation == "发光")

# --- 场景描述 ---
text = g.scene_text()
check("scene text has anchors and relations", "锚点" in text and "关系" in text, text)

# --- to_dict ---
d = g.to_dict()
check("to_dict", len(d["anchors"]) == 4 and len(d["edges"]) == 4)

print(f"\nSAG result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
