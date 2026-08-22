# -*- coding: utf-8 -*-
"""补充验证：consolidation 有变化时仍记录 + add_context 写入情境层"""
import sys, os, tempfile, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
from aeis.core import SpacetimeMemoryEngine

eng = SpacetimeMemoryEngine(db_path=os.path.join(tempfile.mkdtemp(), "t.db"))
store = eng.store

print("=== consolidation 有变化时仍记录 ===")
# 写入高重要度节点 → 巩固时应 rehearsed + 可能 boosted → 落节点
eng.add_perception("重要知识 需要巩固", importance=0.95)
n = store.query_nodes(limit=10)[0]
store.increment_access(n.id)  # 触发 rehearsed
stats = eng.consolidate_cycle(rehearsal_threshold=0.7)
print("stats:", stats)
cons = [x for x in store.query_nodes(limit=100) if "consolidation" in x.tags]
print(f"consolidation 节点数: {len(cons)} (期望 ≥1, 有动作时)")
if cons:
    print("  内容:", cons[0].content[:50])

print("\n=== add_context 写入情境层 ===")
node = eng.add_context("刚才用户提到想学 Rust，这是一个短时会话上下文", importance=0.4)
print("返回节点 layer:", node.layer, "| content:", node.content[:30])
ctx_nodes = store.query_nodes(layer="context")
print("情境层节点数:", len(ctx_nodes))
