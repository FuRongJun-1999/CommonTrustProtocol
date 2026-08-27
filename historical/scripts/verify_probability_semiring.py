# -*- coding: utf-8 -*-
"""verify_probability_semiring.py · 验证「概率论 = 半环运算实例」（用户洞察）
贝叶斯网络信念传播（和积算法）== 初始分布 × 转移矩阵幂（pᵀ·Aᵏ）
→ 概率推理与条件链组合（矩阵/半环图运算）同构"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

# 贝叶斯链：高原(初始0.95) →[P=0.9] 沸点降低 →[P=0.85] 煮不熟
A = np.array([[0, 0.9, 0],
              [0, 0, 0.85],
              [0, 0, 0]], dtype=float)  # 转移矩阵（条件概率）
p = np.array([0.95, 0, 0])  # 初始分布

print("=== 验证：概率论 = 半环运算实例 ===\n")
P2 = p @ np.linalg.matrix_power(A, 2)
expected = 0.95 * 0.9 * 0.85
print(f"sum-product 边缘概率 P(煮不熟) = P(高原)·P(沸点|高原)·P(煮不熟|沸点)")
print(f"  = 0.95 × 0.9 × 0.85 = {expected}")
print(f"信念传播 pᵀ·A²[煮不熟] = {P2[2]}")
print(f"一致: {'✔' if abs(P2[2] - expected) < 1e-9 else '✘'}")
print()
print("→ 贝叶斯网络信念传播（和积算法）= 半环运算：")
print("  乘法 = 链式条件概率组合；加法 = 多路径合并")
print("→ 概率推理与条件链组合（矩阵/半环图运算）同构——")
print("  概率论正是我们半环图运算的一个实例（sum=和，product=乘）")
print()
print("→ 漏掉的信息：概率论还给了我们")
print("  ① 条件独立性（结构学习：哪些条件真的独立）")
print("  ② 信念传播（图上全局信息传播——不止局部 DFS）")
print("  ③ 从数据估计条件概率表（学习）")
print("  ④ 我们的预测误差自动条件化 = 贝叶斯后验更新 P(条件|误差)")
