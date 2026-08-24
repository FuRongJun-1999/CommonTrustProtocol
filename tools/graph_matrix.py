# -*- coding: utf-8 -*-
"""graph_matrix.py · 原型验证「线性代数 = 图运算」（用户洞察 2026-08-23）
核心：图的运算 = 矩阵运算（白箱确定性，零 LLM）——
  ① 因果图 → 邻接矩阵
  ② 矩阵幂 A^k = k 步路径（条件链组合的代数形式，替代/补充 DFS）
  ③ 特征向量中心性 = 图关键节点（幂迭代，零依赖）
  ④ 谱特征值 = 图结构信息（连通性/路径增长）
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')


def graph_to_matrix(nodes, edges):
    """图 → 邻接矩阵（有向，带权=边置信度）
    nodes: [id,...]; edges: [(src, dst, weight),...]"""
    idx = {nid: i for i, nid in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n), dtype=np.float32)
    for src, dst, w in edges:
        if src in idx and dst in idx:
            A[idx[src], idx[dst]] = w
    return A, idx


def k_step_paths(A, k):
    """A^k = k 步路径（路径组合的代数化——条件链组合 = 矩阵乘法）"""
    return np.linalg.matrix_power(A, k)


def reachability(A, max_k):
    """多步可达性：I + A + A² + ... + A^k（路径组合闭包）"""
    n = A.shape[0]
    acc = np.eye(n, dtype=np.float32)
    cur = np.eye(n, dtype=np.float32)
    for _ in range(max_k):
        cur = cur @ A
        acc = acc + cur
    return acc


def eigenvector_centrality(A, iterations=50):
    """特征向量中心性（幂迭代）：关键节点 = 图的主结构
    PageRank 同族——白箱确定性"""
    n = A.shape[0]
    v = np.ones(n, dtype=np.float32) / n
    for _ in range(iterations):
        v = A.T @ v
        norm = np.linalg.norm(v)
        if norm < 1e-12:
            break
        v = v / norm
    return v / (v.sum() + 1e-12)


def path_count_from_matrix(A, src_idx, dst_idx, k):
    """矩阵幂路径计数：A^k[src][dst] = src→dst 的 k 步路径数（加权和）"""
    P = np.linalg.matrix_power(A, k)
    return float(P[src_idx, dst_idx])


if __name__ == "__main__":
    print("=== 原型验证：线性代数 = 图运算（白箱确定性 · 零 LLM） ===\n")

    # 因果图：A→B→C（沸点链）+ A→D（气压支路）
    nodes = ["气压低", "沸点降低", "水提前沸腾", "高原气压低"]
    edges = [
        ("气压低", "沸点降低", 0.9),
        ("沸点降低", "水提前沸腾", 0.85),
        ("气压低", "高原气压低", 0.95),
    ]
    A, idx = graph_to_matrix(nodes, edges)
    print("① 因果图 → 邻接矩阵")
    print("   ", nodes)
    print(A)
    print(f"   稀疏度: {np.count_nonzero(A)}/{A.size} 条边")

    print("\n② 矩阵幂 = 多步路径（条件链组合的代数化）")
    for k in (1, 2, 3):
        P = k_step_paths(A, k)
        nz = [(nodes[i], nodes[j], round(float(P[i, j]), 4))
              for i in range(len(nodes)) for j in range(len(nodes))
              if P[i, j] > 0.01]
        print(f"   A^{k}（{k}步路径）: {nz}")

    print("\n③ 路径组合闭包（可达性：条件链全程）")
    R = reachability(A, 3)
    for i, s in enumerate(nodes):
        reach = [nodes[j] for j in range(len(nodes)) if R[i, j] > 0.01 and i != j]
        if reach:
            print(f"   从「{s}」可达: {reach}")

    print("\n④ 特征向量中心性（关键节点 = 图主结构）")
    # 说明：DAG（有向无环）邻接矩阵是严格三角阵，主特征值=0 → 中心性全 0
    # （数学事实：无环图无谱中心性）。谱分析适用于带反馈环的子图——
    # 用知识环演示：信息差↓ → 信任↑ → 协作↑ → 信息差↓（正反馈环）
    ring_nodes = ["信息差缩小", "信任提升", "协作加深"]
    ring_edges = [("信息差缩小", "信任提升", 0.8),
                  ("信任提升", "协作加深", 0.8),
                  ("协作加深", "信息差缩小", 0.8)]
    R, ridx = graph_to_matrix(ring_nodes, ring_edges)
    rc = eigenvector_centrality(R)
    print(f"   [DAG 谱为 0——无环图无中心性；知识环谱分析:]")
    for nid, score in sorted(zip(ring_nodes, rc), key=lambda x: -x[1]):
        print(f"   {nid}: 中心性={score:.4f}")
    print(f"   （知识环 3 节点中心性相当 → 相互强化的循环结构）")
    print(f"   [原 DAG 谱说明] 严格三角矩阵主特征值=0，中心性=0（数学事实）")

    # 验证：矩阵幂路径 vs DFS 路径（predict_routes 同族结果）
    print("\n⑤ 验证：矩阵路径 = 递归路径（条件链一致性）")
    two_step = path_count_from_matrix(A, idx["气压低"], idx["水提前沸腾"], 2)
    dfs_path = 0.9 * 0.85  # 气压低→沸点降低→水提前沸腾（DFS 链式乘积）
    print(f"   矩阵 A²[气压低][水提前沸腾] = {two_step:.4f} | DFS 链式 = {dfs_path:.4f}")
    print(f"   一致: {'✔' if abs(two_step - dfs_path) < 1e-4 else '✘'}")

    print("\n=== 结论：矩阵运算是图运算的白箱代数化 ===\n"
          "A^k = 条件链组合（递归的代数形式）；特征向量 = 关键节点（谱分析）；\n"
          "CNN 卷积 = 局部邻接矩阵加权和（局部图运算）。三者统一于线性代数。")
