# -*- coding: utf-8 -*-
"""复现报告问题 1 纯回退场景：查询词与所有同义词组零重叠 + 目标节点为新写入
→ LIKE 必落空 → 回退取最旧 500 行 → 新节点被隔离"""
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

# 填充节点先写（占满最旧 500 行）
for i in range(520):
    add(f"填充节点 {i} 一些无关内容", importance=0.1, tags=["filler"])
# 目标节点最后写——rowid 最大，不在回退 LIMIT 500 内；内容词与同义词组零重叠
add("铁钉在潮湿盐水环境中最容易生锈，防锈要隔绝氧气和水", importance=0.9, tags=["rust"])

print("=== 纯回退场景: 新节点 + 零重叠重组短语 ===")
q = "铁钉 生锈 潮湿 盐水"
print("expand terms:", LayeredStore.expand_query_terms(q))
hits = st.search_content(q, limit=5)
for n, s in hits[:3]:
    print(f"  sim={s:.2f} imp={n.importance} | {n.content[:30]}")
print(f"  命中目标节点: {any('铁钉在潮湿' in n.content for n, _ in hits)}")
