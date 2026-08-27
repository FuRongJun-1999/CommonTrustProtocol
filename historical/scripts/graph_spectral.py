# -*- coding: utf-8 -*-
"""graph_spectral.py · 原型验证「傅里叶变换的影响在图上」（用户洞察 2026-08-23）
核心：域变换思想——时域→频域揭示隐藏结构；图上同理——
  ① 图拉普拉斯矩阵 L = D - A（图的结构算子）
  ② 特征分解 L = UΛUᵀ → 图傅里叶变换（GFT）：信号 → 谱域
  ③ 谱域滤波（低通=保留全局结构/高通=局部细节）→ 逆变换
  ④ 语义时空图信号：低频分量=全局共识知识，高频=局部差异
统一：图卷积（GCN）= 谱域滤波；CNN = 规则网格上的谱域滤波特例。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')


def adjacency_from_edges(nodes, edges):
    idx = {nid: i for i, nid in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n), dtype=np.float32)
    for src, dst, w in edges:
        if src in idx and dst in idx:
            A[idx[src], idx[dst]] = w
            A[idx[dst], idx[src]] = w  # 无向（谱分析用对称矩阵）
    return A, idx


def laplacian(A):
    """图拉普拉斯 L = D - A（图的结构算子——二阶差分算子，图上'导数'）"""
    D = np.diag(A.sum(axis=1))
    return D - A


def graph_fourier_transform(L):
    """图傅里叶变换：L = UΛUᵀ——特征向量=图的谱基（频域），特征值=频率"""
    eigvals, eigvecs = np.linalg.eigh(L)  # 对称矩阵特征分解（升序=低频到高频）
    return eigvals, eigvecs


def gft_signal(signal, U):
    """正变换：图信号 → 谱域系数（投影到谱基）"""
    return U.T @ signal


def igft_signal(coeffs, U):
    """逆变换：谱域系数 → 图信号"""
    return U @ coeffs


def spectral_filter(coeffs, eigvals, kind="lowpass", cutoff_ratio=0.3):
    """谱域滤波：低通=保留低频（全局结构）/高通=高频（局部细节）"""
    n = len(eigvals)
    cut = max(1, int(n * cutoff_ratio))
    out = coeffs.copy()
    if kind == "lowpass":
        out[cut:] = 0.0
    elif kind == "highpass":
        out[:cut] = 0.0
    return out


if __name__ == "__main__":
    print("=== 原型验证：图傅里叶变换（傅里叶的影响在图上 · 零 LLM） ===\n")

    # 语义知识图：两簇知识（A 簇：气压/沸点/煮饭；B 簇：光/植物/光合）
    nodes = ["气压低", "沸点降低", "煮不熟", "光照", "光合作用", "植物生长"]
    edges = [
        ("气压低", "沸点降低", 0.9), ("沸点降低", "煮不熟", 0.85),
        ("气压低", "煮不熟", 0.5),
        ("光照", "光合作用", 0.9), ("光合作用", "植物生长", 0.85),
        ("光照", "植物生长", 0.5),
    ]
    A, idx = adjacency_from_edges(nodes, edges)
    L = laplacian(A)
    print("① 图拉普拉斯 L = D - A（图的结构算子，图上'二阶导数'）")
    print(L.round(2))

    eigvals, U = graph_fourier_transform(L)
    print("\n② 图傅里叶变换：特征值（频率）=", [round(v, 3) for v in eigvals])
    n_components = int(np.sum(np.abs(eigvals) < 1e-6))
    print(f"   特征值0的个数 = 连通分量数 = {n_components}（两簇知识 = 2 个连通分量）")

    # 图信号：某节点激活（如「气压低」=1，其余0）
    signal = np.zeros(len(nodes), dtype=np.float32)
    signal[idx["气压低"]] = 1.0
    coeffs = gft_signal(signal, U)
    print("\n③ 图信号「气压低」→ 谱域系数（能量分布）")
    print("   系数=", [round(c, 3) for c in coeffs])

    # 低通滤波：保留全局结构（知识簇的主传播路径）
    low = igft_signal(spectral_filter(coeffs, eigvals, "lowpass"), U)
    high = igft_signal(spectral_filter(coeffs, eigvals, "highpass"), U)
    print("\n④ 谱域滤波 → 逆变换")
    print("   低通（全局结构）:", {nodes[i]: round(float(low[i]), 3)
          for i in range(len(nodes)) if abs(low[i]) > 0.05})
    print("   高通（局部细节）:", {nodes[i]: round(float(high[i]), 3)
          for i in range(len(nodes)) if abs(high[i]) > 0.05})

    # 语义：低频分量 = 同簇知识传播（气压低→沸点→煮不熟都在低通响应中）
    print("\n⑤ 语义解读：低通保留「气压低」所在知识簇的全局传播"
          "（A 簇成员均响应）；高通保留簇内差异（细节）")
    print("   → 域变换揭示隐藏结构：知识的'频率'=在图上的传播尺度（全局/局部）")

    # 验证：图卷积 = 谱域滤波（GCN 思想）
    print("\n⑥ 图卷积 = 谱域滤波（GCN）：x' = U·g(Λ)·Uᵀ·x")
    g = np.exp(-eigvals)  # 谱域核（低频权重高——平滑）
    x = np.zeros(len(nodes), dtype=np.float32)
    x[idx["光照"]] = 1.0
    x_conv = U @ (g * (U.T @ x))
    print("   光照激活 → 图卷积传播:",
          {nodes[i]: round(float(x_conv[i]), 3)
           for i in range(len(nodes)) if abs(x_conv[i]) > 0.05})
    print("   （光照 → 光合 → 植物生长 B 簇传播——谱域平滑=图上消息传递）")
