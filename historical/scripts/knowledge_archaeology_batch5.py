# -*- coding: utf-8 -*-
"""知识考古 · 批次5 补卡（2026-08-21 · 最后一批）

#2 AI补齐（7卡）+ #11 博弈论与决策（5卡）+ #12 演化与模因（4卡）= 16 卡

审核纪律（沿用）：
  - 物理基底可验证（Transformer注意力/纳什均衡/自然选择——客观定义）
  - 拒绝主观词（独立成词的 好/坏/我觉得/应该）
  - 每条带审核说明 + 条件空间 + 学科域/学段标签
  - 不宣称首创：既有学术成果，贡献在纳入协议坐标系
"""
import sys, io, json, sqlite3, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
DB_W = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"

ENTRIES = [
    # ============ #2 人工智能补齐 ============
    ("注意力机制", "注意力机制：根据相关性给输入分配权重——查询Q与键K的相似度决定值V的加权和（softmax）。Transformer的核心，让模型聚焦相关部分。对应CSPMN只匹配激活条件空间。",
     "人工智能", "E4", "Vaswani 2017 Attention is All You Need，可验证"),
    ("Transformer", "Transformer：基于自注意力+前馈的序列模型架构——多头注意力并行捕捉不同关系、位置编码注入顺序、残差连接+层归一化稳定训练。是当代大语言模型的基础架构。",
     "人工智能", "E4", "Vaswani 2017 Transformer论文，可验证"),
    ("扩散模型", "扩散模型：前向逐步加噪直到纯噪声，反向学习去噪（score匹配）恢复数据——训练时预测噪声，生成时从噪声逐步去噪。图像生成的主流（Stable Diffusion）。",
     "人工智能", "E4", "Ho 2020 DDPM，可验证"),
    ("强化学习", "强化学习：智能体通过与环境交互学习策略最大化累计奖励——状态/动作/奖励/策略/价值函数；Q-learning/策略梯度/PPO。奖励设计要防奖励黑客（生成器与验证器分离的学术对照）。",
     "人工智能", "E4", "Sutton-Barto 强化学习标准教材，可验证"),
    ("元学习", "元学习（learning to learn）：从多个任务中学习如何快速学习新任务——MAML（模型无关元学习）、课程学习（由易到难安排任务）。是Ornith自生成课程的学术底座。",
     "人工智能", "E4", "Finn 2017 MAML，可验证"),
    ("神经缩放定律", "神经缩放定律（scaling law）：模型性能随参数量/数据量/计算量呈幂律提升（loss ∝ N^α）——Kaplan 2020。涌现能力：规模跨过阈值后出现新能力。",
     "人工智能", "E4", "Kaplan 2020缩放定律，可验证"),
    ("对抗鲁棒性", "对抗鲁棒性：模型对微小扰动（对抗样本）的稳定性——FGSM/PGD攻击、对抗训练防御。是「可验证边界」的AI版（模型不能只对训练分布有效）。",
     "人工智能", "E4", "Goodfellow 2014对抗样本，可验证"),
    # ============ #11 博弈论与决策 ============
    ("机制设计", "机制设计：给定目标反向设计规则使理性参与者激励相容——揭示原理（真实报告为占优策略）、VCG机制。是协议设计侧（博弈论的设计面）。",
     "博弈论", "E4", "Hurwicz 1972机制设计理论，可验证"),
    ("贝叶斯决策", "贝叶斯决策：基于后验概率和损失函数做最优决策——期望损失最小化的行动。决策规则由先验+似然+损失共同决定（协议元公理4效用最大化的形式化）。",
     "博弈论", "E4", "贝叶斯决策理论（Wald 1950），可验证"),
    ("效用理论", "效用理论：理性选择按期望效用最大化——冯诺依曼-摩根斯坦效用（对不确定结果的偏好排序）。风险偏好（风险中性/厌恶/寻求）影响决策。对应协议元公理4。",
     "博弈论", "E4", "von Neumann-Morgenstern 1944效用理论，可验证"),
    ("合作博弈", "合作博弈：参与者通过结盟合作分配总收益——夏普利值（按边际贡献分配）、核（稳定联盟集）。是蜂群协作/信任演化的分配数学。",
     "博弈论", "E4", "Shapley 1953夏普利值，可验证"),
    ("囚徒困境", "囚徒困境：个体理性导致集体非最优——双方背叛是纳什均衡但合作对双方更好。重复博弈（无限次）可达成合作（以牙还牙策略）。是信任/合作演化的经典模型。",
     "博弈论", "E4", "Tucker 1950囚徒困境，可验证"),
    # ============ #12 演化与模因 ============
    ("合作演化", "合作演化：利他行为如何在自然选择中存活——亲缘选择（Hamilton规则：rB>C）、互惠利他（重复博弈）、群体选择。是信任演化的生物学基础。",
     "演化", "E4", "Hamilton 1964亲缘选择，可验证"),
    ("模因论", "模因论：文化传播的最小单位——模因（meme）经复制/变异/选择演化，类似基因但载体是观念/行为。对应协议价值观-模因演化系统（0.5）。",
     "演化", "E4", "Dawkins 1976《自私的基因》模因概念，可验证"),
    ("复制子方程", "复制子方程：群体中策略/类型的频率动态——dx_i/dt = x_i(f_i - f̄)，适应度高于平均的占比增长。是演化博弈/价值观传播的数学。",
     "演化", "E4", "Taylor-Jonker 1978复制子方程，可验证"),
    ("适应度景观", "适应度景观：基因型/策略映射到适应度的地形——峰谷结构（局部最优陷阱）、适应度丘陵（平滑搜索）。是「找到规则攻坚判断」（梯度搜索）的生物学版。",
     "演化", "E4", "Wright 1932适应度景观，可验证"),
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
                             "existence_constraint": "AI/博弈论/演化标准定义"}, ensure_ascii=False)
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
