# -*- coding: utf-8 -*-
"""graph_matrix.py · 原型验证「线性代数 = 图运算」（用户洞察 2026-08-23）
核心：图的运算 = 矩阵运算（白箱确定性，零 LLM）——
  ① 因果图 → 邻接矩阵
  ② 矩阵幂 A^k = k 步路径（条件链组合的代数形式，替代/补充 DFS）
  ③ 特征向量中心性 = 图关键节点（幂迭代，零依赖）
  ④ 谱特征值 = 图结构信息（连通性/路径增长）
"""
import sys
import random
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


# ============ 六、随机条件图一致性验证（GPT 第 7 点建议） ============
def random_condition_graph(n_nodes, edge_prob=0.4, seed=0):
    """随机条件图：n 节点有向图，边带置信度（0.3~1.0）"""
    rng = random.Random(seed)
    nodes = [f"N{i}" for i in range(n_nodes)]
    edges = []
    for i in range(n_nodes):
        for j in range(n_nodes):
            if i != j and rng.random() < edge_prob:
                edges.append((nodes[i], nodes[j], round(rng.uniform(0.3, 1.0), 2)))
    return nodes, edges


def dfs_path_weights(adj, src, dst, k):
    """DFS 枚举 src→dst 的恰好 k 步路径 → 权重和（程序化图表达）"""
    total = 0.0

    def walk(node, depth, prod):
        nonlocal total
        if depth == k:
            if node == dst:
                total += prod
            return
        for nxt, w in adj.get(node, {}).items():
            walk(nxt, depth + 1, prod * w)

    walk(src, 0, 1.0)
    return total


def verify_dfs_matrix_consistency(n_graphs=40, n_nodes=(3, 8), k_max=4, tol=1e-5):
    """大规模随机验证：DFS 路径权重和 == 矩阵幂 A^k（严格一致）
    → 递归条件组合 ↔ 矩阵运算 的代数等价（工程结论）"""
    checked = 0
    mismatches = []
    for g in range(n_graphs):
        n = random.randint(*n_nodes)
        nodes, edges = random_condition_graph(n, seed=g * 7 + 1)
        A, idx = graph_to_matrix(nodes, edges)
        adj = {}
        for src, dst, w in edges:
            adj.setdefault(src, {})[dst] = w
        # 随机采样 src/dst/k 组合
        samples = min(12, n * n)
        for _ in range(samples):
            src = random.choice(nodes)
            dst = random.choice(nodes)
            if src == dst:
                continue
            k = random.randint(1, k_max)
            d = dfs_path_weights(adj, src, dst, k)
            m = path_count_from_matrix(A, idx[src], idx[dst], k)
            checked += 1
            if abs(d - m) > tol:
                mismatches.append((g, src, dst, k, d, m))
                if len(mismatches) >= 5:
                    return checked, mismatches
    return checked, mismatches


# ============ 七、条件传播矩阵（半环雏形：元素=(置信度, 条件集合)） ============
class CondEntry:
    """条件矩阵元素：(置信度, 条件集合)——条件传播
    乘法：置信度相乘 + 条件并集（沿链传播条件）
    加法：多路径合并——条件取并集（任一链成立即可），置信度取 max（保底语义）"""

    def __init__(self, conf=0.0, conds=None):
        self.conf = conf
        self.conds = frozenset(conds or ())

    def __mul__(self, other):
        return CondEntry(self.conf * other.conf, self.conds | other.conds)

    def __add__(self, other):
        # 多路径合并：条件并集（析取），置信度取较大（确定性路径优先）
        return CondEntry(max(self.conf, other.conf), self.conds | other.conds)


def condition_propagation(nodes, edges_with_conds, k):
    """条件化邻接矩阵 A(C) 的 k 步组合——条件沿路径传播（半环运算雏形）
    edges_with_conds: [(src, dst, conf, cond_str), ...]"""
    idx = {nid: i for i, nid in enumerate(nodes)}
    n = len(nodes)
    M = [[CondEntry() for _ in range(n)] for _ in range(n)]
    for src, dst, conf, cond in edges_with_conds:
        M[idx[src]][idx[dst]] = CondEntry(conf, {cond})
    # 半环矩阵乘法（k 步）：C[i][j] = Σ_l M[i][l]⊗M[l][j]
    def semiring_mul(X, Y):
        Z = [[CondEntry() for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                acc = CondEntry()
                for l in range(n):
                    acc = acc + (X[i][l] * Y[l][j])
                Z[i][j] = acc
        return Z

    result = M
    for _ in range(k - 1):
        result = semiring_mul(result, M)
    return result, idx


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

    print("\n⑥ 大规模随机验证：DFS 路径权重和 == 矩阵幂 A^k（GPT 第 7 点建议）")
    checked, mismatches = verify_dfs_matrix_consistency(n_graphs=40)
    if not mismatches:
        print(f"   {checked} 组 (图,源,目标,k) 采样全部一致 ✔"
              f"——递归条件组合 ↔ 矩阵运算 代数等价成立")
    else:
        for m in mismatches[:3]:
            print(f"   ✘ 不一致: 图{m[0]} {m[1]}→{m[2]} k={m[3]} DFS={m[4]:.5f} 矩阵={m[5]:.5f}")

    print("\n⑦ 条件传播矩阵（半环雏形：元素=(置信度, 条件集合)）")
    cond_nodes = ["高原", "沸点降低", "煮不熟", "用高压锅", "能煮熟"]
    cond_edges = [
        ("高原", "沸点降低", 0.9, "气压低"),
        ("沸点降低", "煮不熟", 0.85, "水温不足100°C"),
        ("高原", "用高压锅", 0.8, "需要增压"),
        ("用高压锅", "能煮熟", 0.9, "沸点升到120°C"),
        ("沸点降低", "能煮熟", 0.3, "？"),
    ]
    CM, cidx = condition_propagation(cond_nodes, cond_edges, 2)
    print(f"   A(C)²[高原][煮不熟] = 置信度 {CM[cidx['高原']][cidx['煮不熟']].conf:.3f}"
          f" 条件 {sorted(CM[cidx['高原']][cidx['煮不熟']].conds)}")
    print(f"   A(C)²[高原][能煮熟] = 置信度 {CM[cidx['高原']][cidx['能煮熟']].conf:.3f}"
          f" 条件 {sorted(CM[cidx['高原']][cidx['能煮熟']].conds)}")
    print("   （条件沿路径传播：矩阵元素 = (置信度, 条件集合)——条件链组合的代数表达）")

    print("\n=== 结论：矩阵运算是图运算的白箱代数化 ===\n"
          "A^k = 条件链组合（递归的代数形式）；特征向量 = 关键节点（谱分析）；\n"
          "CNN 卷积 = 局部邻接矩阵加权和（局部图运算）。三者统一于线性代数。")
