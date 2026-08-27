# -*- coding: utf-8 -*-
"""知识考古 · 批次4 补卡（2026-08-21）

#1 数学补齐（10卡·工程价值优先）+ #10 统计学习理论（5卡）= 15 张卡 → 图谱

数学选卡原则（荣：傅里叶背后还有一大批工程上极具价值的数学）：
  按协议关联度排序——矩阵分解/CSPMN 直接相关、优化/学习数学、贝叶斯/信任、
  谱图论/图谱结构、不动点/递归、蒙特卡洛/主动探测、凸优化/KKT 配套。

审核纪律（沿用）：
  - 物理基底可验证（SVD定理/中心极限定理/VC维——客观定义）
  - 拒绝主观词（独立成词的 好/坏/我觉得/应该）
  - 每条带审核说明 + 条件空间 + 学科域/学段标签
  - 不宣称首创：既有学术成果，贡献在纳入协议坐标系
"""
import sys, io, json, sqlite3, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

ENTRIES = [
    # ============ #1 数学补齐（工程价值优先） ============
    ("奇异值分解", "奇异值分解（SVD）：任意矩阵 A = UΣVᵀ——U/V 正交阵，Σ 对角奇异值（非负降序）。奇异值度量矩阵在每个方向上的能量；PCA/压缩/推荐系统/伪逆的数学基础（CSPMN 矩阵乘法的分解工具）。",
     "数学", "E4", "SVD定理是线性代数标准内容，可验证"),
    ("梯度下降法", "梯度下降：沿目标函数负梯度方向迭代更新参数（θ←θ-η∇L）使损失最小化——η为学习率。随机梯度下降SGD用单样本梯度近似。是信息差驱动学习（预测误差→调整）的优化实现。",
     "数学", "E4", "优化理论标准算法，可验证"),
    ("贝叶斯推断", "贝叶斯推断：后验 ∝ 似然 × 先验——P(θ|D) ∝ P(D|θ)·P(θ)，观测数据后更新信念。对应协议置信概率P_trust的贝叶斯更新（信任随证据修订）。",
     "数学", "E4", "贝叶斯定理（Bayes 1763），可验证"),
    ("中心极限定理", "中心极限定理：大量独立同分布随机变量的和（或均值）近似正态分布，无论原分布形态——n→∞时标准化和收敛到标准正态。是大规模观测聚合的统计基础（D_norm 的统计意义）。",
     "数学", "E4", "中心极限定理是概率论核心定理，可验证"),
    ("拉普拉斯变换", "拉普拉斯变换：时域函数 → 复频域 F(s)=∫f(t)e^(-st)dt，把微分方程变代数方程——线性系统分析与控制理论的核心工具（传递函数/稳定性判定）。",
     "数学", "E4", "拉普拉斯变换是工程数学标准工具，可验证"),
    ("希尔伯特空间", "希尔伯特空间：完备的内积空间——向量有长度/夹角/正交概念，函数可作向量（L²空间）。量子力学/信号处理/机器学习核方法的数学基底（条件空间的几何表述）。",
     "数学", "E4", "泛函分析标准概念（Hilbert），可验证"),
    ("蒙特卡洛方法", "蒙特卡洛方法：用大量随机采样近似复杂积分/期望——大数定律保证收敛（样本均值→期望）。粒子滤波/强化学习/数值模拟的基石（主动盲区探测的采样思路）。",
     "数学", "E4", "蒙特卡洛方法（Metropolis 1949），可验证"),
    ("不动点定理", "不动点定理（Banach压缩映射）：完备度量空间上的压缩映射有唯一不动点，迭代逼近——x_{n+1}=f(x_n)收敛到f的不动点。递归方程/自指/迭代算法的解存在性保证（协议递归验证的数学底）。",
     "数学", "E4", "Banach 1922不动点定理，可验证"),
    ("谱图论", "谱图论：用图拉普拉斯矩阵的特征值/特征向量研究图结构——特征值编码连通性/聚类/分割，特征向量给出图的谱嵌入。知识图谱结构（条件空间关系）的数学分析工具。",
     "数学", "E4", "谱图理论（Chung 1997），可验证"),
    ("凸优化", "凸优化：目标函数凸+约束集凸——局部最优即全局最优，有高效算法（梯度/内点法）。KKT条件给出最优性判定。是约束优化/条件空间匹配的数学基础。",
     "数学", "E4", "凸优化理论（Boyd 2004），可验证"),
    # ============ #10 统计学习理论 ============
    ("VC维", "VC维：模型能打散（shatter）的最大样本数——度量假设空间复杂度。VC维越高模型越灵活但越易过拟合。是「可验证边界」的数学（过拟合=固化错误路径）。",
     "统计学习", "E4", "Vapnik-Chervonenkis 1971 VC维，可验证"),
    ("偏差方差权衡", "偏差-方差权衡：泛化误差 = 偏差² + 方差 + 不可约噪声——偏差高=欠拟合（模型太简单），方差高=过拟合（太复杂）。最优模型在两者平衡点。对应条件空间泛化。",
     "统计学习", "E4", "偏差方差分解（Geman 1992），可验证"),
    ("PAC学习", "PAC学习（可能近似正确）：给定样本量 m，学习算法以高概率输出误差≤ε的假设——样本复杂度 m 的界。是「可验证承诺」的数学（白箱可复现性）。",
     "统计学习", "E4", "Valiant 1984 PAC学习框架，可验证"),
    ("正则化", "正则化：在损失函数加惩罚项约束模型复杂度——L1（稀疏，特征选择）、L2（权重收缩）、早停（提前停止训练）。防过拟合=防固化错误路径（协议：技能附条件防过拟合）。",
     "统计学习", "E4", "正则化理论（Tikhonov），可验证"),
    ("交叉验证与信息准则", "模型选择工具：交叉验证（数据切分评估泛化）、AIC（赤池信息准则）/BIC（贝叶斯信息准则，惩罚复杂度）。是验证单元（模型选择的证据标准）。",
     "统计学习", "E4", "Akaike 1974 AIC/Schwarz 1978 BIC，可验证"),
]

REJECT = ("我觉得", "我认为", "最好", "美丽", "值得", "重要", "必须",
          "所有人", "总是", "从不")


def audit(ans, reason):
    for w in REJECT:
        if w in ans:
            return False, f"含主观词「{w}」"
    for w in ("好", "坏"):
        for m in re.finditer(w, ans):
            i = m.start()
            prev = ans[i - 1] if i > 0 else " "
            nxt = ans[i + 1] if i + 1 < len(ans) else " "
            if (prev in "，。；、（）\s" or not prev.isalpha()) and \
                    (nxt in "，。；、（）\s" or not nxt.isalpha()):
                return False, f"含独立主观词「{w}」"
    if len(ans) < 20:
        return False, "答案过短"
    if not reason:
        return False, "缺审核说明"
    return True, reason


def main():
    for db in (DB, DB_W):
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        now = time.time()
        added = skipped = rejected = 0
        for name, ans, domain, edu, reason in ENTRIES:
            ok, note = audit(ans, reason)
            if not ok:
                print(f"  ✗ 拒绝 [{domain}] {name[:14]}：{note}")
                rejected += 1
                continue
            cur.execute("SELECT COUNT(*) FROM nodes WHERE content LIKE ?",
                        ('%' + ans[:20] + '%',))
            if cur.fetchone()[0] > 0:
                print(f"  — 已存在 [{domain}] {name[:14]}")
                skipped += 1
                continue
            node_id = f"kp_archaeo_{int(time.time()*1000)}"
            cs = json.dumps({"observation_position": "知识考古补全",
                             "observation_tool": "前沿既有知识（审核后）",
                             "time_window": [now, now + 31536000],
                             "existence_constraint": "数学/统计学习标准定义"}, ensure_ascii=False)
            sa = json.dumps({"name": name, "domain": domain, "level": 4,
                             "status": "verified",
                             "response": {"trigger": [name]}}, ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, spatial_coordinates, temporal_coordinate, "
                "condition_space, importance, confidence, layer, access_count, last_access, created_at, "
                "tags, semantic_coordinates, state_attributes, entity_id) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (node_id, ans, "text", "{}", now, cs, 0.8, 0.9, "knowledge", 0, now, now,
                 json.dumps(["知识飞轮", "知识考古", f"domain:{domain}", f"edu:{edu}",
                             "verified", "前沿知识"], ensure_ascii=False),
                 "{}", sa, None))
            added += 1
            print(f"  ✓ [{domain}] {name[:16]} → {ans[:36]}...")
        conn.commit()
        print(f"库 {db[-36:]}: 添加 {added} / 跳过 {skipped} / 拒绝 {rejected}")
        conn.close()


if __name__ == "__main__":
    main()
