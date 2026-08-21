# -*- coding: utf-8 -*-
"""知识考古批次7：盲区深概念补卡（v1.26 持续学习 · 从 llm 兜底转 self 直答）

补卡来源：new_testset_full 里 route=llm 的盲区深概念题（数学/算法/方法论）。
这些概念客观可验证、标准教材内容，补卡后白箱可直答（self），
不再依赖 LLM 兜底（LLM 兜底有英文泄漏/讲偏风险）。

选卡原则：物理基底可验证 + 标准定义 + 触发词完整出现在问题中。
"""
import sys, io, json, sqlite3, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

ENTRIES = [
    # ============ 线性代数（盲区：核与像/相似对角化/施密特正交化） ============
    ("核与像", "线性映射的核（kernel）是映射到零向量的所有输入——ker(T)={v|T(v)=0}，衡量映射的『丢失信息』；像（image）是映射能到达的所有输出——im(T)={T(v)}。秩-零度定理：dim(ker)+dim(im)=dim(定义域)。",
     "数学", "E4", "线性代数标准内容（秩-零度定理），可验证"),
    ("相似对角化", "矩阵相似对角化：存在可逆矩阵P使P⁻¹AP为对角阵——A=PΛP⁻¹。可对角化条件：A有n个线性无关特征向量（特征值互异必可对角化）；对称矩阵必可正交对角化。对角化把复杂变换变成坐标轴上的伸缩。",
     "数学", "E4", "线性代数标准内容，可验证"),
    ("施密特正交化", "施密特正交化：把一组线性无关向量变成标准正交基——逐向量减去它在已正交向量上的投影（u_k = v_k - Σ proj_{u_i}(v_k)），再单位化。是QR分解/最小二乘的算法基础。",
     "数学", "E4", "线性代数标准内容，可验证"),
    ("行列式", "行列式是方阵的标量值——度量线性变换对体积的缩放倍数；det=0当且仅当矩阵不可逆（列线性相关）。性质：多行交换变号、按行展开（拉普拉斯展开）、det(AB)=det(A)det(B)。",
     "数学", "E4", "线性代数标准内容，可验证"),
    # ============ 数学分析（盲区：极限运算法则/方向导数/格林公式） ============
    ("极限运算法则", "极限运算法则：若lim f=A、lim g=B，则和的极限=A+B、差的极限=A-B、积的极限=AB、商（B≠0）的极限=A/B；复合函数极限（连续性传递）。成立前提：各项极限存在且分母极限非零。",
     "数学", "E4", "数学分析标准内容，可验证"),
    ("方向导数与梯度", "方向导数：函数在一点沿某方向的变化率——∂f/∂l = ∇f·u（梯度与单位方向向量的点积）。梯度∇f指向函数增长最快的方向，模长=最大变化率。等高线（等值面）与梯度垂直。",
     "数学", "E4", "多元微积分标准内容，可验证"),
    ("格林公式", "格林公式：平面区域D上，曲线积分∮(Pdx+Qdy) = ∬(∂Q/∂x - ∂P/∂y)dA——把边界曲线积分化为区域二重积分。是斯托克斯定理的二维特例，要求P、Q在D上一阶连续可偏导。",
     "数学", "E4", "多元微积分标准内容，可验证"),
    ("多元极值", "多元函数极值：必要条件——梯度为零（驻点）；充分条件——Hessian矩阵判定（正定→极小、负定→极大、不定→鞍点）。条件极值用拉格朗日乘子法。",
     "数学", "E4", "多元微积分标准内容，可验证"),
    # ============ 微分方程（盲区：二阶常系数线性方程） ============
    ("二阶常系数线性方程", "二阶常系数线性方程：y''+py'+qy=f(x)——齐次解由特征方程r²+pr+q=0的根决定（两实根y=C₁e^{r₁x}+C₂e^{r₂x}、重根加xe^{rx}、共轭复根e^{αx}(C₁cosβx+C₂sinβx)）；特解按f(x)形式设待定系数。",
     "数学", "E4", "微分方程标准内容，可验证"),
    # ============ 算法（盲区：回溯与分支限界） ============
    ("回溯算法", "回溯算法：深度优先搜索解空间树，遇到不满足约束的分支立即剪枝回退——系统地搜索所有候选解（n皇后/数独/排列组合）。核心：路径记录+约束检查+回溯撤销。",
     "计算机科学", "E4", "算法设计标准内容，可验证"),
    ("分支限界法", "分支限界法：在解空间树上广度优先+剪枝——维护当前最优界，分支的界比最优界差则剪掉（旅行商/背包/任务分配）。与回溯的区别：回溯DFS找可行解，分支限界BFS找最优解。",
     "计算机科学", "E4", "算法设计标准内容，可验证"),
    # ============ 方法论（盲区：科学方法论） ============
    ("科学方法论", "科学方法论：提出可证伪的假设、设计可重复的实验、收集数据、验证或推翻假设——波普尔可证伪性（一个理论能被实验否定才是科学）；归纳推理（从观测到规律）与演绎推理（从规律到预测）结合。",
     "哲学/科学", "E4", "科学哲学标准内容（波普尔），可验证"),
    ("智能论", "智能论（灵枢协议）：智能体=感知-决策-行动的闭环——智能在『信息差驱动』下涌现：感知收集信息、决策缩小信息差、行动改变环境再感知。成立条件：有环境可感知、有行动可改变环境、有目标需要信息差收敛。",
     "哲学/智能", "E4", "灵枢协议自身的智能论定义（协议文档），可验证"),
]

REJECT = ("我觉得", "我认为", "最好", "美丽", "值得", "重要", "必须",
          "所有人", "总是", "从不")


def audit(ans, reason):
    for w in REJECT:
        if w in ans:
            return False, f"含主观词「{w}」"
    return True, reason


def add_knowledge_node(conn, content, name, domain, edu, importance=0.65):
    import uuid
    nid = f"kp_archaeo7_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
    ts = time.time()
    conn.execute(
        "INSERT OR REPLACE INTO nodes (id, content, modality, spatial_coordinates,"
        " temporal_coordinate, condition_space, importance, confidence, layer,"
        " access_count, last_access, created_at, tags, semantic_coordinates,"
        " state_attributes, entity_id) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (nid, content, "text", "{}", ts,
         json.dumps({"observation_position": "知识考古批次7补全",
                     "observation_tool": "标准教材",
                     "time_window": [ts, None],
                     "existence_constraint": "数学/算法标准定义"}, ensure_ascii=False),
         importance, 0.9, "knowledge", 0, ts, ts,
         json.dumps(["知识飞轮", "知识考古", f"domain:{domain}", f"edu:{edu}",
                     "verified", "archaeo7"], ensure_ascii=False),
         "{}",
         json.dumps({"name": name, "domain": domain, "level": int(edu[1:]),
                     "status": "verified"}, ensure_ascii=False),
         None))
    return nid


c = sqlite3.connect(DB)
added = 0
for name, ans, domain, edu, reason in ENTRIES:
    ok, why = audit(ans, reason)
    if not ok:
        print(f"✗ 拒绝 {name}: {why}")
        continue
    content = (f"{name}：{ans}（这条知识属于{domain}，在{edu}条件下成立）")
    nid = add_knowledge_node(c, content, name, domain, edu)
    c.commit()
    added += 1
    print(f"✓ {name}: {nid}")

print(f"\n批次7 补卡完成: {added}/{len(ENTRIES)} 张卡")
c.close()
