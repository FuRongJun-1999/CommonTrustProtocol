# -*- coding: utf-8 -*-
"""复现报告问题 1：重组短语检索失效 + 新节点不可召回"""
import sys, os, tempfile, time, uuid
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
from aeis.core import LayeredStore, STNode, ConditionSpace

db = os.path.join(tempfile.mkdtemp(), "test_recall.db")
st = LayeredStore(db)
CS = ConditionSpace(observation_position="t", observation_tool="t",
                    time_window=(time.time(), time.time() + 3600),
                    existence_constraint="test")

def add(content, importance=0.5, tags=None):
    n = STNode(id=uuid.uuid4().hex[:12], content=content, modality="text",
               spatial_coordinates={}, temporal_coordinate=time.time(),
               condition_space=CS, importance=importance, tags=tags or [])
    return st.add_node(n)

add("数据库连接池耗尽时客户端重试超时，需要合理配置超时时间", importance=0.9, tags=["db"])
for i in range(520):
    add(f"填充节点 {i} 一些无关内容", importance=0.1, tags=["filler"])

print("=== 测试1: 重组短语召回 ===")
q = "数据库 连接池 超时 重试"
hits = st.search_content(q, limit=5)
for n, s in hits[:3]:
    print(f"  sim={s:.2f} imp={n.importance} | {n.content[:30]}")

print("\n=== 测试2: 连续短语召回（LIKE 命中路径） ===")
hits2 = st.search_content("数据库连接池", limit=5)
for n, s in hits2[:3]:
    print(f"  sim={s:.2f} imp={n.importance} | {n.content[:30]}")

print("\n=== 测试3: expand_query_terms 分词 ===")
print("  terms:", LayeredStore.expand_query_terms("数据库 连接池 超时 重试"))
