# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import semantic_translate as st

chain = st.gen_followup("为什么天空是蓝色的？", "天空呈蓝色是因为瑞利散射", limit=6, depth=3)
print("深度 3 追问链:")
for i, f in enumerate(chain, 1):
    print(f"  {i}. {f['q']} ({f['concept']})")

# 用户点追问后继续：什么是波长？→ 前置链
chain2 = st.gen_followup("什么是波长？", "波长是波在一个周期内传播的距离", limit=3, depth=2)
print("\n波长 深度 2 追问:")
for f in chain2:
    print(f"  - {f['q']} ({f['concept']})")
