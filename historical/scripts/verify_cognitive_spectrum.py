# -*- coding: utf-8 -*-
"""verify_cognitive_spectrum.py · 验证「白箱认知结构的频域：预测误差 = 高频信号」
（GPT 建议 2026-08-23）
假设：知识图的低频 = 全局结构（基础条件/共识知识），高频 = 局部变化/异常/误差。
验证：把「异常/误差节点」作为图信号 → 图傅里叶 → 谱域——
  异常信号能量集中在高频（局部变化）vs 正常知识信号在低频（全局结构）。
意义：预测误差 = 高频认知信号（已有结构无法解释的局部变化）——
  频谱可以定位「认知结构无法解释之处」= 盲区/误差的谱域信号。
"""
import sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')


def laplacian_eigen(A):
    D = np.diag(A.sum(axis=1))
    L = D - A
    eigvals, eigvecs = np.linalg.eigh(L)
    return eigvals, eigvecs


def frequency_energy_ratio(signal, U, eigvals, cutoff_ratio=0.4):
    """信号的高频能量占比：谱域系数中高频部分能量 / 总能量"""
    coeffs = U.T @ signal
    n = len(eigvals)
    cut = int(n * cutoff_ratio)
    total = float(np.sum(coeffs ** 2)) + 1e-12
    high = float(np.sum(coeffs[cut:] ** 2))
    return high / total, coeffs


if __name__ == "__main__":
    print("=== 验证：认知结构频域——预测误差 = 高频信号 ===\n")

    # 知识图：A簇(气压/沸点/煮饭 紧密) + B簇(光/光合/植物 紧密) + 异常节点(弱连接)
    nodes = ["气压低", "沸点降低", "煮不熟",
             "光照", "光合作用", "植物生长",
             "异常知识X"]  # 异常：与 A 簇弱连接（局部变化）
    n = len(nodes)
    A = np.zeros((n, n), dtype=np.float32)
    pairs = [
        (0, 1, 0.9), (1, 2, 0.85), (0, 2, 0.5),     # A 簇
        (3, 4, 0.9), (4, 5, 0.85), (3, 5, 0.5),     # B 簇
        (0, 6, 0.2),                                  # 异常节点弱连接（高频）
    ]
    for i, j, w in pairs:
        A[i, j] = A[j, i] = w

    eigvals, U = laplacian_eigen(A)
    print("① 知识图：A簇+B簇（紧密）+ 异常节点X（仅 0.2 弱连接）")
    print(f"   特征值（频率）: {[round(v, 2) for v in eigvals]}")

    # ② 图信号对比：异常节点激活 vs 知识簇激活（全局结构信号）
    sig_abnormal = np.zeros(n, dtype=np.float32)
    sig_abnormal[nodes.index("异常知识X")] = 1.0
    # 正常知识信号 = A 簇整体激活（知识簇的全局结构 → 低频主导）
    sig_normal = np.zeros(n, dtype=np.float32)
    for name in ("气压低", "沸点降低", "煮不熟"):
        sig_normal[nodes.index(name)] = 1.0

    hi_abn, c_abn = frequency_energy_ratio(sig_abnormal, U, eigvals)
    hi_norm, c_norm = frequency_energy_ratio(sig_normal, U, eigvals)

    print("\n② 图信号 → 谱域（高频能量占比）")
    print(f"   异常节点信号: 高频占比 = {hi_abn:.3f}（与主结构失配 → 高频相对高）")
    print(f"   知识簇信号:   高频占比 = {hi_norm:.3f}（全局结构 → 低频主导）")
    print(f"   异常高频 > 知识簇高频: {'✔' if hi_abn > hi_norm else '✘'} "
          f"({hi_abn:.3f} vs {hi_norm:.3f})")

    # ③ 谱域定位异常：高通滤波 → 恢复异常节点位置
    def highpass_recover(signal, U, eigvals, cutoff_ratio=0.4):
        coeffs = U.T @ signal
        n = len(eigvals)
        cut = int(n * cutoff_ratio)
        coeffs[:cut] = 0.0  # 只留高频
        return U @ coeffs

    recovered = highpass_recover(sig_abnormal, U, eigvals)
    top = sorted(((nodes[i], float(recovered[i])) for i in range(n)),
                 key=lambda x: -abs(x[1]))[:3]
    print("\n③ 高通滤波 → 逆变换（谱域定位异常）")
    print(f"   异常响应最强节点: {[(t, round(v, 3)) for t, v in top]}")
    ok_loc = top[0][0] == "异常知识X"
    print(f"   异常被高频分量定位: {'✔' if ok_loc else '✘'}")

    print("\n=== 结论 ===\n"
          "知识图的频域：低频 = 全局结构（紧密知识簇），高频 = 局部变化（异常/误差）。\n"
          "预测误差 = 高频认知信号——频谱可以定位「认知结构无法解释之处」\n"
          "（盲区/误差的谱域信号）：高频能量高 = 该处是局部异常/遗漏条件。")
