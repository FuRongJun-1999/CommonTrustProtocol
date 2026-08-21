# -*- coding: utf-8 -*-
"""验证 recall_plot 与 _recall_mem 的 plot 优先召回。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\aeis")
from aeis.roleplay_chat import LingshuChat

rid = "role-1787113781424"
chat = LingshuChat(data_dir=r"D:\Program Files\2_ai\knowledge-base\roleplay_data")

# 1. 直接查 plot 节点
agent = chat.rp._agent(rid)
plots = agent.recall_plot(limit=6)
print(f"=== recall_plot: {len(plots)} 条 ===")
for n in plots:
    print(f"  imp={n.importance} | {(n.content or '')[:70]}")
    print(f"      tags={n.tags}")

# 2. _recall_mem 是否 plot 优先
print("\n=== _recall_mem('现在该怎么办') ===")
for m in chat._recall_mem("plot-recall-1", "现在该怎么办", limit=6, role_id=rid):
    print("  -", m[:80])
chat.close()
