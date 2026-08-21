# -*- coding: utf-8 -*-
"""图谱边显式化（v1.25 · 2026-08-21 · 知识考古复盘工程化 #3）

89 张考古卡 → 四大深层结构簇内/跨簇建边：
  - causal（簇内因果链）：信息差簇的香农熵→KL→信息瓶颈→信道容量等
  - similar（同簇同构 + 跨簇协议同构）：簇内同构（Kuramoto≈神经振荡），
    跨簇协议同构（预测编码≈卡尔曼≈自适应滤波=信息差驱动族）

复盘四簇：
  簇1 信息差=结构偏离：香农熵/互信息/KL散度/信道容量/率失真/信息瓶颈/
    Kolmogorov复杂度/奈奎斯特采样/数据压缩熵界/预测编码/卡尔曼滤波/
    自适应滤波/梯度下降/贝叶斯推断/交叉验证
  簇2 同步=相位锁定：Kuramoto/神经振荡/混沌的边缘/自组织临界性
  簇3 信任=贝叶斯更新：贝叶斯推断/合作演化/囚徒困境/高斯过程/内稳态
  簇4 条件空间=结构坐标系：谱图论/概率图模型/希尔伯特空间/微分几何流形/
    张量分解/网络科学/信息几何相关
"""
import sys, io, json, sqlite3, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

# 四簇卡名 → 建边规则
CLUSTER1_INFO_GAP = [
    "香农熵", "互信息", "KL散度", "信道容量", "率失真理论", "信息瓶颈",
    "Kolmogorov复杂度", "奈奎斯特采样定理", "数据压缩熵界",
    "预测编码", "卡尔曼滤波", "自适应滤波", "梯度下降法", "贝叶斯推断",
    "交叉验证与信息准则", "信息差",
]
CLUSTER2_SYNC = ["Kuramoto模型", "神经振荡", "混沌的边缘", "自组织临界性",
                 "混沌与蝴蝶效应", "耦合振子", "相位同步"]
CLUSTER3_TRUST = ["贝叶斯推断", "合作演化", "囚徒困境", "高斯过程", "内稳态",
                  "信任", "合作博弈", "复制子方程"]
CLUSTER4_SPACE = ["谱图论", "概率图模型", "希尔伯特空间", "微分几何与流形",
                  "张量分解", "网络科学", "信息瓶颈", "凸优化", "最优传输",
                  "奇异值分解", "数值线性代数"]


def name2id(cur, name):
    r = cur.execute(
        "SELECT id FROM nodes WHERE state_attributes LIKE ? LIMIT 1",
        ('%"name": "' + name + '"%',)).fetchone()
    return r[0] if r else None


def add_edge(cur, src, tgt, rel, conf, weight, evidence, now, seq):
    if not src or not tgt or src == tgt:
        return False, seq
    # 去重
    dup = cur.execute(
        "SELECT 1 FROM edges WHERE source_id=? AND target_id=? AND relation_type=?",
        (src, tgt, rel)).fetchone()
    if dup:
        return False, seq
    seq += 1
    eid = f"edge_archaeo_{int(now)}{seq:04d}"
    cur.execute(
        "INSERT INTO edges (id, source_id, target_id, relation_type, condition_space, "
        "confidence, weight, verified, created_at, last_verified, source_evidence) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (eid, src, tgt, rel, "{}", conf, weight, 1, now, now, evidence))
    return True, seq


def main():
    now = time.time()
    for db in (DB, DB_W):
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        added = 0
        seq = 0
        # 簇内 causal 链（信息差簇：熵→散度→编码→压缩的因果）
        c1_causal = [
            ("香农熵", "KL散度", "熵是KL散度的特例（P=均匀分布时D_KL=H）"),
            ("香农熵", "数据压缩熵界", "熵定义无损压缩下界"),
            ("KL散度", "信息瓶颈", "信息瓶颈用互信息/KL优化表示"),
            ("互信息", "信息瓶颈", "信息瓶颈最大化互信息"),
            ("信道容量", "率失真理论", "信道容量=最大互信息，率失真=最小码率"),
            ("数据压缩熵界", "Kolmogorov复杂度", "香农熵（统计）与K复杂度（算法）互补"),
            ("预测编码", "卡尔曼滤波", "预测编码=层级预测误差，卡尔曼=预测-更新状态估计"),
            ("卡尔曼滤波", "自适应滤波", "都是预测误差驱动更新的滤波族"),
            ("预测编码", "梯度下降法", "都按误差/梯度调整（预测误差最小化）"),
            ("贝叶斯推断", "交叉验证与信息准则", "后验更新=观测证据修正（BIC=贝叶斯模型选择）"),
        ]
        # 簇内 similar（同构）
        c_similar = [
            ("Kuramoto模型", "神经振荡", "耦合振子锁相=脑节律同步"),
            ("混沌的边缘", "自组织临界性", "临界态/相变区同构"),
            ("合作演化", "囚徒困境", "亲缘/互惠=重复博弈合作的演化解释"),
            ("谱图论", "概率图模型", "图结构=条件独立结构"),
            ("希尔伯特空间", "微分几何与流形", "内积几何=流形几何的线性局部"),
            ("张量分解", "奇异值分解", "SVD是二阶张量（矩阵）分解，张量分解是推广"),
            ("最优传输", "KL散度", "分布距离两种度量：OT几何/Wasserstein vs KL"),
        ]
        # 跨簇协议同构（similar：指向同一协议结构）
        cross_similar = [
            ("预测编码", "信息差", "预测误差=信息差的神经对应"),
            ("卡尔曼滤波", "信息差", "预测-更新=信息差驱动"),
            ("自适应滤波", "信息差", "误差梯度调整=信息差驱动学习"),
            ("Kuramoto模型", "神经振荡", "蜂群同步/脑节律同构"),
            ("贝叶斯推断", "内稳态", "信念更新/状态维持都是动态调整"),
            ("谱图论", "网络科学", "图谱结构分析"),
        ]
        # 先建簇内 causal
        for s, t, ev in c1_causal:
            ok, seq = add_edge(cur, name2id(cur, s), name2id(cur, t), "causal",
                               0.8, 0.9, ev, now, seq)
            if ok:
                added += 1
        # 簇内 similar
        for s, t, ev in c_similar:
            ok, seq = add_edge(cur, name2id(cur, s), name2id(cur, t), "similar",
                               0.7, 0.8, ev, now, seq)
            if ok:
                added += 1
        # 跨簇协议同构
        for s, t, ev in cross_similar:
            ok, seq = add_edge(cur, name2id(cur, s), name2id(cur, t), "similar",
                               0.75, 0.85, ev, now, seq)
            if ok:
                added += 1
        conn.commit()
        total = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        print(f"库 {db[-30:]}: 新增边 {added}，边总数 {total}")
        conn.close()


if __name__ == "__main__":
    main()
