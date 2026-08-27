# -*- coding: utf-8 -*-
"""知识考古 · 批次6 补卡（2026-08-21 · 工程数学拓展）

荣：「傅里叶背后还有一大批工程上极具价值的数学」——批次4已补基础10卡，
本批补工程应用层数学（复分析/群论/随机微分/张量/最优传输/数值方法等）。

选卡原则：工程价值 + 协议关联（对称性=CSPMN权值共享、最优传输=条件空间
距离、概率图模型=图谱结构、排队论=维生资源调度、MCMC=盲区探测采样）。

审核纪律（沿用）：
  - 物理基底可验证（留数定理/伊藤引理/最优传输——客观定义）
  - 拒绝主观词（独立成词的 好/坏/我觉得/应该）
  - 每条带审核说明 + 条件空间 + 学科域/学段标签
  - 不宣称首创：既有学术成果，贡献在纳入协议坐标系
"""
import sys, io, json, sqlite3, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

ENTRIES = [
    # ============ 工程数学拓展 ============
    ("复分析", "复分析：研究复变函数——解析函数（可微即无穷可微）、留数定理（围道积分=极点留数和，算实积分利器）、共形映射（保角变换）。信号处理/控制理论/电磁场的数学基底。",
     "数学", "E4", "复分析是数学物理标准领域，可验证"),
    ("群论与对称性", "群论：研究对称性的代数结构——群（封闭/结合/单位/逆元）、子群/陪集/同态、表示论（群作用在向量空间）。晶体/粒子物理/编码理论的基础；对应CNN权值共享（平移对称性）的数学。",
     "数学", "E4", "群论标准内容（Galois/Cayley），可验证"),
    ("随机微分方程", "随机微分方程（SDE）：带随机噪声的微分方程——布朗运动、伊藤引理（随机链式法则）、几何布朗运动（金融）。是连续时间随机过程的建模工具（信息差的连续时间演化）。",
     "数学", "E4", "伊藤清1944伊藤引理，可验证"),
    ("生成函数", "生成函数：把数列编码为幂级数系数——F(x)=Σa_n x^n，用代数操作推导数列性质（递推/组合计数）。是组合数学的桥梁工具（序列的结构编码）。",
     "数学", "E4", "生成函数是组合数学标准工具，可验证"),
    ("有限元方法", "有限元方法（FEM）：把连续域离散为有限单元，用分片多项式逼近偏微分方程解——刚度矩阵+载荷向量。工程仿真（结构/流体/热）的主流数值方法（物理基底真执行的数值化）。",
     "数学", "E4", "FEM是计算力学标准方法，可验证"),
    ("共轭梯度法", "共轭梯度法：求解大型对称正定线性方程组（或凸二次优化）的迭代法——沿共轭方向搜索，n步内收敛。大规模优化/深度学习训练的数值核心（CSPMN矩阵计算的工程实现）。",
     "数学", "E4", "Hestenes-Stiefel 1952共轭梯度，可验证"),
    ("张量分解", "张量分解：多维数组的低秩分解——CP分解（秩1分量和）、Tucker分解（核张量+因子矩阵）。多维数据分析（推荐/EEG/图像）工具；对应条件空间的高维表示。",
     "数学", "E4", "Kolda-Bader 2009张量分解综述，可验证"),
    ("概率图模型", "概率图模型（PGM）：用图表示变量间条件独立——贝叶斯网络（有向）、马尔可夫随机场（无向）；推断（消息传递/变分）与学习。是知识图谱/条件空间关系的概率版。",
     "数学", "E4", "Koller-Friedman PGM教材，可验证"),
    ("高斯过程", "高斯过程（GP）：函数空间上的分布——任意有限点集联合高斯，由均值函数+核函数（协方差）定义。贝叶斯优化/回归的工具（函数级的不确定性量化）。",
     "数学", "E4", "Rasmussen-Williams GP教材，可验证"),
    ("最优传输", "最优传输（OT）：最小代价把一种分布搬运成另一种——Wasserstein距离（地球搬运工距离）、Kantorovich对偶。分布间距离的度量（条件空间距离的深化，比KL更几何）。",
     "数学", "E4", "Kantorovich 1942最优传输，可验证"),
    ("微分几何与流形", "微分几何：研究光滑流形上的几何——切空间/黎曼度量/曲率；信息几何（概率分布族是流形，Fisher度量）。是条件空间几何表述的深化（知识状态=流形上的点）。",
     "数学", "E4", "微分几何标准内容，可验证"),
    ("数值线性代数", "数值线性代数：矩阵计算的稳定高效算法——QR分解/LU分解/条件数（数值稳定性）/奇异值计算。是CSPMN矩阵运算的工程基础（精度与效率的保证）。",
     "数学", "E4", "Trefethen数值线性代数教材，可验证"),
    ("短时傅里叶变换", "短时傅里叶变换（STFT）：加窗分段做FFT，得到时频图——同时看频率随时间变化（弥补FFT无时间分辨率）。语音/音频分析工具；对应五层记忆的时频联合视角。",
     "信号处理", "E4", "STFT是信号处理标准工具，可验证"),
    ("排队论", "排队论：研究等待系统（到达/服务/队列）的数学——M/M/1队列（泊松到达+指数服务）、利特尔法则（L=λW）。资源调度/维生系统能耗管理的数学（代谢预算分配）。",
     "数学", "E4", "排队论（Erlang 1909），可验证"),
    ("马尔可夫链蒙特卡洛", "马尔可夫链蒙特卡洛（MCMC）：构造马尔可夫链使平稳分布为目标分布，采样逼近复杂分布——Metropolis-Hastings、吉布斯采样。贝叶斯推断/盲区探测采样的工具（主动探测的采样数学）。",
     "数学", "E4", "Metropolis 1953/Hastings 1970，可验证"),
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
                             "existence_constraint": "工程数学标准定义"}, ensure_ascii=False)
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
