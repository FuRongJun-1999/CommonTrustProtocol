# -*- coding: utf-8 -*-
"""知识递归追问 · PREREQ 前置链构建器（v1.26 · 荣设计）

机制：回答「为什么天空是蓝色的」后，路由表沿知识依赖链生成递归追问
（天空蓝→瑞利散射→波长→波→振动…）。

前置链来源（荣选定：从因果边推导 + 人工补关键链）：
  1. 遍历图谱 causal 边（source→target = source 是更基础概念）：
     若 source/target 名映射到规范词 → prereq[target].append(source)
  2. 人工补高频概念的确定性前置链（自动推导漏掉的）
"""
import sqlite3, json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import semantic_translate as st

DB = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"
c = sqlite3.connect(DB)

# 1. 从 causal 边推导
prereq = {}  # target规范词 -> [source规范词...]


def norm_name(nid):
    r = c.execute("SELECT state_attributes, content FROM nodes WHERE id=?", (nid,)).fetchone()
    if not r:
        return None
    try:
        d = json.loads(r[0] or "{}")
        nm = d.get("name")
        if nm and len(nm) >= 2 and nm in st.DOMAIN_SYNONYM_CLUSTERS:
            return nm
    except Exception:
        pass
    return None


derived = 0
for s, t, rel in c.execute(
        "SELECT source_id, target_id, relation_type FROM edges WHERE relation_type='causal'"):
    sn = norm_name(s)
    tn = norm_name(t)
    if sn and tn and sn != tn:
        prereq.setdefault(tn, [])
        if sn not in prereq[tn]:
            prereq[tn].append(sn)
            derived += 1
print(f"从 causal 边推导: {derived} 条前置（{len(prereq)} 概念）")

# 2. 人工补关键链（确定性高依赖，自动推导可能漏）
MANUAL = {
    "天空蓝色": ["瑞利散射", "波长"],
    "瑞利散射": ["波长", "光"],
    "波长": ["波", "频率"],
    "波": ["振动"],
    "沸腾": ["沸点与气压", "分子热运动"],
    "沸点与气压": ["气压", "分子热运动"],
    "光合作用": ["细胞", "叶绿体"],
    "细胞": ["细胞核"],
    "重力": ["质量", "万有引力"],
    "自由落体": ["重力", "加速度"],
    "惯性": ["质量", "牛顿第一定律"],
    "氧化": ["化学反应", "氧"],
    "溶解": ["分子", "浓度"],
    "浮力": ["重力", "密度", "液体压强"],
    "大气压": ["气压", "分子"],
    "声音传播": ["振动", "介质"],
    "瑞利散射": ["波长", "散射"],
    "折射": ["光", "介质", "波长"],
    "反射": ["光", "镜面"],
    "电流": ["电压", "电荷", "导体"],
    "电压": ["电势", "电荷"],
    "杠杆": ["力矩", "支点"],
    "递归": ["函数", "基例"],
    "大语言模型": ["Transformer", "统计学习", "参数"],
    "Transformer": ["注意力机制", "神经网络"],
    "注意力机制": ["神经网络"],
    "梯度下降法": ["导数", "损失函数"],
    "贝叶斯推断": ["概率论", "先验", "后验"],
    "涌现": ["复杂系统", "自组织"],
    "熵": ["概率", "信息"],
    "香农熵": ["概率", "对数"],
    "奇点": ["引力", "时空"],
    "量子纠缠": ["量子叠加", "量子力学"],
    "光合作用": ["植物", "光"],
    "心电图": ["心脏", "电信号"],
    "基因": ["DNA", "染色体"],
    "遗传": ["基因", "DNA"],
    "免疫系统": ["细胞", "病原体"],
    "黑洞": ["引力", "逃逸速度", "事件视界"],
    "能带": ["能级", "晶体", "量子力学"],
    "放射性衰变": ["原子核", "同位素"],
    "辩证法": ["矛盾", "对立统一"],
    "唯物史观": ["生产力", "生产关系", "经济基础"],
    "科学方法论": ["可证伪性", "归纳推理", "演绎推理"],
    "智能论": ["信息差", "感知", "行动"],
    "条件空间": ["存在约束", "观测位置"],
    "信息差": ["信息", "不确定性"],
    "负反馈": ["系统", "稳态"],
    "内稳态": ["负反馈", "体温", "血糖"],
    "预测编码": ["预测误差", "层级结构", "信息差"],
    "工作记忆": ["注意", "短期记忆"],
    "元认知": ["认知", "监控"],
    "认知偏差": ["启发式", "系统1"],
    "二阶控制论": ["控制论", "观察者"],
    "Kuramoto模型": ["耦合振子", "相位"],
    "自组织临界性": ["幂律", "沙堆模型"],
    "标度律": ["幂律", "指数"],
    "谱图论": ["特征值", "图", "拉普拉斯矩阵"],
    "凸优化": ["凸函数", "可行域", "梯度"],
    "奇异值分解": ["特征值", "正交矩阵", "矩阵"],
    "蒙特卡洛方法": ["随机采样", "大数定律"],
    "不动点定理": ["压缩映射", "完备空间"],
    "VC维": ["打散", "假设空间"],
    "正则化": ["过拟合", "损失函数"],
    "囚徒困境": ["博弈", "背叛", "合作"],
    "纳什均衡": ["博弈", "策略", "最优反应"],
    "效用理论": ["偏好", "期望"],
    "强化学习": ["奖励", "策略", "价值函数"],
    "元学习": ["任务分布", "快速适应"],
    "扩散模型": ["去噪", "加噪", "概率"],
    "对抗鲁棒性": ["对抗攻击", "鲁棒性"],
    "神经网络": ["神经元", "权重", "激活函数"],
    "统计学习": ["样本", "泛化", "经验风险"],
    "缩放定律": ["参数", "数据量", "计算量"],
    "频率": ["周期", "振动"],
    "振动": ["周期", "介质"],
    "光": ["电磁波", "光子"],
    "散射": ["光", "粒子", "波长"],
    "电磁波": ["电场", "磁场", "频率"],
    "光子": ["量子", "能量"],
    "能量": ["功", "焦耳"],
}
for k, v in MANUAL.items():
    prereq.setdefault(k, [])
    for p in v:
        if p not in prereq[k]:
            prereq[k].append(p)
print(f"人工补链后: {len(prereq)} 概念有前置")

# 3. 保存到 semantic_translate 可见的 JSON（供 gen_followup 运行时加载）
out_path = os.path.join(os.path.dirname(st.__file__), "prereq_map.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(prereq, f, ensure_ascii=False, indent=1)
print(f"已存 {out_path}")

# 展示关键链
print("\n=== 示例链 ===")
for k in ("天空蓝色", "瑞利散射", "波长", "大语言模型", "黑洞"):
    print(f"{k} -> {prereq.get(k, [])}")
c.close()
