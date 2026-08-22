# -*- coding: utf-8 -*-
"""复现报告问题 1 核心场景：目标节点是【新写入】的（rowid 大），回退取最旧 500 行 → 无法召回"""
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

# 先写 520 个填充节点（占满"最旧 500 行"）
for i in range(520):
    add(f"填充节点 {i} 一些无关内容", importance=0.1, tags=["filler"])
# 目标节点【最后写】——rowid 最大，不在回退的 LIMIT 500 内
add("数据库连接池耗尽时客户端重试超时，需要合理配置超时时间", importance=0.9, tags=["db"])

print("=== 核心场景: 新节点 + 重组短语（应命中目标节点） ===")
q = "数据库 连接池 超时 重试"
hits = st.search_content(q, limit=5)
for n, s in hits[:3]:
    print(f"  sim={s:.2f} imp={n.importance} | {n.content[:30]}")
print(f"  命中目标节点: {any('数据库连接池' in n.content for n, _ in hits)}")
