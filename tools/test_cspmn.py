# -*- coding: utf-8 -*-
"""CSPMN 测试：CPU 后端检索 / 盲区注入 / 信息差驱动深度决策"""
import sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Program Files\2_ai\knowledge-base")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")

from cspmn import CSPMN
from neural_retrieve import NeuralRetriever

nr = NeuralRetriever()
net = CSPMN(backend="cpu")
print("=== CSPMN 初始化 ===")
info = net.info()
print(f"  子实例: {info['sub_instances']} | 维度: {info['dim']} | 后端: {info['backend']}")

print("\n=== 1. 真实检索（P1+P2+P3） ===")
qs = ["三角形的内角和是多少度？", "为什么天空是蓝色的？", "什么是递归",
      "什么是函数呀", "我今天好难过", "下期彩票中奖号码是多少？"]
for q in qs:
    qv = nr.embed(q)
    r = net.search(qv, limit=3)
    top = r["hits"][0] if r["hits"] else None
    print(f"  {q[:14]:<16} → top={top['name'][:18] if top else 'NONE'} "
          f"score={r['top_score']:.3f} depth={r['depth']} "
          f"盲区={'⚠️' if r['blind_spot'] else '✓'}")

print("\n=== 2. 盲区注入（追加子实例） ===")
# 模拟新知识卡（向量用 bge 编码「番茄炒蛋为什么会出水」）
new_vec = nr.embed("番茄炒蛋为什么会出水")
before = net.info()["sub_instances"]
r = net.inject(new_vec, "生活常识·番茄炒蛋出水", domain="生活常识")
print(f"  注入前 {before} → 注入后 {r['N_after']} | status={r['status']}")

print("\n=== 3. 信息差驱动调用深度（荣：信息差小就不深调用） ===")
cases = [
    ("大信息差", 0.7, 0.0),
    ("中信息差", 0.45, 0.0),
    ("小信息差+高匹配", 0.2, 0.5),
    ("信息差收敛（自维持）", 0.2, -0.05),
]
for label, dn, trend in cases:
    net.set_gap(dn, trend)
    d = net.depth_for(top=0.7 if dn <= 0.3 else 0.3)
    print(f"  {label:<14} D_norm={dn} trend={trend:+.2f} → 深度 {d}")

print("\n=== 4. 性能（3030 规模 CPU） ===")
qv = nr.embed("三角形的内角和是多少度？")
t0 = time.time()
for _ in range(100):
    net.search(qv, limit=5)
print(f"  搜索全链路: {(time.time()-t0)/100*1000:.2f} ms/次")

print("\nPASS: CSPMN 测试完成")
