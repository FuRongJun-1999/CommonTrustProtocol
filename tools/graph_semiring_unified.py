# -*- coding: utf-8 -*-
"""graph_semiring_unified.py · 验证「半环统一：同一图结构，换代数 = 换推理模式」
（GPT 建议 2026-08-23）
同一条件图 A→B→C，四种半环各自给出正确推理：
  ① 概率半环（×, +）   → 可能性传播 sum-product = 0.72675
  ② 最大半环（×, max） → 最可信路径 max-product = 0.765
  ③ 布尔半环（AND, OR）→ 可达性 = True
  ④ 条件半环（conf×+conds∪, max+conds∪）→ 条件满足传播 = {气压低, 水温不足}
意义：规则不是孤立存在，而是在不同条件空间中成立——推理模式 = 图结构 × 代数。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')


class Semiring:
    """半环：(combine=链式组合, merge=多路径合并, zero=空, label)"""

    def __init__(self, combine, merge, zero, label):
        self.combine = combine  # 乘法（沿链组合）
        self.merge = merge      # 加法（多路径合并）
        self.zero = zero
        self.label = label


# 四种半环
PROB = Semiring(lambda a, b: a * b, lambda a, b: a + b, 0.0, "概率半环(可能性传播)")
MAXP = Semiring(lambda a, b: a * b, max, 0.0, "最大半环(最可信路径)")
BOOL = Semiring(lambda a, b: a and b, lambda a, b: a or b, False, "布尔半环(可达性)")
COND = Semiring(lambda a, b: (a[0] * b[0], a[1] | b[1]),
                lambda a, b: (max(a[0], b[0]), a[1] | b[1]),
                (0.0, frozenset()), "条件半环(条件满足传播)")


def semiring_propagate(nodes, edges, sr, k, src, dst):
    """通用半环传播：src → dst 的 k 步路径组合+合并（信念传播同族）"""
    idx = {nid: i for i, nid in enumerate(nodes)}
    n = len(nodes)
    # 邻接（半环元素）
    adj = [[sr.zero for _ in range(n)] for _ in range(n)]
    for a, b, w, *cond in edges:
        if sr is COND:
            adj[idx[a]][idx[b]] = (w, frozenset(cond[0] if cond else ()))
        else:
            adj[idx[a]][idx[b]] = w
    # 初始状态：src 为 one（路径起点），其余 zero
    one = 1.0 if sr is not BOOL else True
    if sr is COND:
        one = (1.0, frozenset())
    state = [sr.zero for _ in range(n)]
    state[idx[src]] = one
    # 传播 k 步
    for _ in range(k):
        nxt = [sr.zero for _ in range(n)]
        for i in range(n):
            if state[i] == sr.zero:
                continue
            for j in range(n):
                if adj[i][j] == sr.zero:
                    continue
                nxt[j] = sr.merge(nxt[j], sr.combine(state[i], adj[i][j]))
        state = nxt
    return state[idx[dst]]


if __name__ == "__main__":
    print("=== 验证：半环统一——同一图结构 × 不同代数 = 不同推理模式 ===\n")
    # 同一条件图：高原 →沸点降低→ 煮不熟（条件链）
    nodes = ["高原", "沸点降低", "煮不熟"]
    edges = [
        ("高原", "沸点降低", 0.9),
        ("沸点降低", "煮不熟", 0.85),
    ]
    # 初始状态：P(高原)=0.95（贝叶斯网络初始证据）
    print("图：高原 --0.9--> 沸点降低 --0.85--> 煮不熟；初始 P(高原)=0.95\n")

    # ① 概率半环（含初始证据——用权重扩展：起点权重=0.95）
    edges_p = [("高原", "沸点降低", 0.9 * 0.95), ("沸点降低", "煮不熟", 0.85)]
    p = semiring_propagate(nodes, edges_p, PROB, 2, "高原", "煮不熟")
    print(f"① {PROB.label}: P(煮不熟) = {p:.5f}（期望 0.95×0.9×0.85=0.72675）"
          f" {'✔' if abs(p-0.72675)<1e-4 else '✘'}")

    # ② 最大半环：最可信路径
    m = semiring_propagate(nodes, edges, MAXP, 2, "高原", "煮不熟")
    print(f"② {MAXP.label}: max 路径权重 = {m:.4f}（期望 0.9×0.85=0.765）"
          f" {'✔' if abs(m-0.765)<1e-4 else '✘'}")

    # ③ 布尔半环：可达性
    b = semiring_propagate(nodes, edges, BOOL, 2, "高原", "煮不熟")
    print(f"③ {BOOL.label}: 高原→煮不熟可达 = {b} {'✔' if b else '✘'}")

    # ④ 条件半环：条件满足传播
    edges_c = [("高原", "沸点降低", 0.9, ["气压低"]),
               ("沸点降低", "煮不熟", 0.85, ["水温不足100°C"])]
    c = semiring_propagate(nodes, edges_c, COND, 2, "高原", "煮不熟")
    print(f"④ {COND.label}: 置信度 {c[0]:.3f} 条件 {sorted(c[1])}"
          f"（期望 {0.765} + {{气压低, 水温不足100°C}}）"
          f" {'✔' if abs(c[0]-0.765)<1e-4 and c[1]==frozenset({'气压低','水温不足100°C'}) else '✘'}")

    print("\n=== 结论 ===\n"
          "同一图结构（条件链）换代数 = 换推理模式：\n"
          "  概率半环=可能性传播 / 最大半环=最可信路径 / 布尔半环=可达性 / 条件半环=条件满足传播\n"
          "→ 「规则不是孤立存在，而是在不同条件空间中成立」——推理 = 图结构 × 代数\n"
          "→ 条件路由表可以按需求选代数（概率/最可信/可达/条件），同一图底座")
