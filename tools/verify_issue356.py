# -*- coding: utf-8 -*-
"""验证 问题3/5/6 修复"""
import sys, os, tempfile
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
from aeis.core import LayeredStore, SpacetimeMemoryEngine as MemoryEngine, STNode, ConditionSpace
import time, uuid

db = os.path.join(tempfile.mkdtemp(), "test_fix.db")
eng = MemoryEngine(db_path=db)
store = eng.store
CS = ConditionSpace(observation_position="t", observation_tool="t",
                    time_window=(time.time(), time.time() + 3600),
                    existence_constraint="test")

def add(content, importance=0.5):
    n = STNode(id=uuid.uuid4().hex[:12], content=content, modality="text",
               spatial_coordinates={}, temporal_coordinate=time.time(),
               condition_space=CS, importance=importance)
    return store.add_node(n)

print("=== 问题3: consolidation 无变化不落节点 ===")
add("一个普通节点", importance=0.5)
before = len(store.query_nodes(limit=1000))
# 空库巩固（无 rehearsed/boosted/degraded/compressible 动作）
stats = eng.consolidate_cycle()
after = len(store.query_nodes(limit=1000))
print(f"  巩固后节点数变化: {before} -> {after} (期望不变)")
cons_nodes = [n for n in store.query_nodes(limit=1000) if "consolidation" in n.tags]
print(f"  consolidation 节点数: {len(cons_nodes)} (期望 0)")

print("\n=== 问题6: recall 权重可配置 ===")
add("关于数据库连接池超时的知识", importance=0.9)
add("一个完全无关的填充", importance=0.1)
r1 = eng.recall("数据库 连接池 超时", limit=3)
r2 = eng.recall("数据库 连接池 超时", limit=3, w_sim=1.0, w_importance=0.0, w_recency=0.0)
print(f"  默认权重调用成功: {len(r1)} 条 (期望 >0)")
print(f"  纯相似度权重调用成功: {len(r2)} 条 (期望 >0)")
print(f"  两个调用 top1 相同: {r1[0][0].id == r2[0][0].id if r1 and r2 else 'N/A'}")

print("\n=== 问题5: MCP add_context 工具注册 ===")
from aeis.mcp.server import _tools
names = [t["name"] for t in _tools()]
print(f"  add_context 在工具集: {'add_context' in names}")
print(f"  工具总数: {len(names)}")
