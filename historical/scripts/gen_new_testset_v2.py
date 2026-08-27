# -*- coding: utf-8 -*-
"""新测试集 v2 扩展：三来源增量（与 v1 不重复），v1+v2 → 全量 ~150 题。

策略：v1 已覆盖「已能直答」的部分（72/72），v2 目标 = 探测更深盲区：
  1. 盲区剩余：模板类高等数学/线代/群论（因式分解/矩阵分解/格林公式/若尔当/
     施密特正交化…）+ 非模板类（统计学/存在论/伽罗瓦/环公理/冯诺依曼…）
  2. 真实对话弱命中剩余：再取 20 条知识类
  3. 考古子概念：批次1-5 的 74 卡的子概念问题（熵/傅里叶/注意力/强化学习…）
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

# ===== 来源一：盲区增量（避开 v1 的 20 条） =====
blind = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\tools\newset_blindspot_source.json", encoding="utf-8"))
import random
random.seed(20260821)
v1_sel = []
for b in blind:
    if b["q"].endswith("在什么条件下成立？") and len(v1_sel) >= 6:
        continue
    v1_sel.append(b)
    if len(v1_sel) >= 20:
        break
v1_q = {b["q"] for b in v1_sel}

# 盲区 v2 选择：模板类数学/线代/群论（高价值盲区）+ 非模板类高 dnorm
v2_blind = []
math_tmpl = ["因式分解定理", "矩阵分解", "极限运算法则", "换元积分", "分部积分",
             "定积分概念", "微积分基本定理", "偏导数", "方向导数与梯度", "二重积分",
             "一阶微分方程", "二阶常系数线性方程", "曲面积分", "循环群", "代数扩张",
             "秩零度定理", "基与维数", "若尔当标准形", "施密特正交化", "对称变换",
             "函数极限", "求导法则", "凹凸性与拐点", "全微分", "多元极值", "格林公式",
             "斯托克斯公式", "常数项级数", "线性空间定义", "最小多项式", "双线性函数"]
for tm in math_tmpl:
    q = f"{tm}在什么条件下成立？"
    if q not in v1_q:
        v2_blind.append({"q": q, "kind": "条件", "dnorm": 0.74,
                         "blindspot_source": "BS-QUERY-WEAK"})
nontmpl = [b for b in blind if not b["q"].endswith("在什么条件下成立？")
           and b["q"] not in v1_q]
nontmpl.sort(key=lambda x: -x["dnorm"])
for b in nontmpl[:20]:
    v2_blind.append({"q": b["q"], "kind": b["kind"], "dnorm": b["dnorm"],
                     "blindspot_source": b["blindspot_source"]})
print(f"盲区 v2: {len(v2_blind)} 题")

# ===== 来源二：真实对话弱命中剩余 =====
real = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\tools\newset_realdialogue_source.json", encoding="utf-8"))
real_know = [r for r in real if r["cat"] in ("知识问答", "条件判断", "编程语言", "协议认知", "生活常识")]
# v1 用了前 30（gen_new_testset 里 real_know[:30] 按原序）
v2_real = real_know[30:55]
print(f"真实对话 v2: {len(v2_real)} 题")
for r in v2_real:
    print(f"    {r['q'][:44]}")

# ===== 来源三：考古子概念（批次1-5 卡 → 子概念问题） =====
arch_v2 = [
    # 信息论（批次1）
    {"q": "什么是KL散度？", "cat": "知识问答", "objective": True, "keys": ["KL", "信息损失", "距离"], "source": "考古-信息论"},
    {"q": "信道容量是什么意思？", "cat": "知识问答", "objective": True, "keys": ["信道容量", "最大信息率"], "source": "考古-信息论"},
    {"q": "率失真理论解决什么问题？", "cat": "知识问答", "objective": True, "keys": ["率失真", "压缩", "失真"], "source": "考古-信息论"},
    # 复杂系统（批次1/2）
    {"q": "什么是混沌？", "cat": "知识问答", "objective": True, "keys": ["混沌", "确定性", "敏感"], "source": "考古-复杂系统"},
    {"q": "什么是蝴蝶效应？", "cat": "知识问答", "objective": True, "keys": ["蝴蝶效应", "初始条件", "敏感"], "source": "考古-复杂系统"},
    {"q": "什么是自组织临界性？", "cat": "知识问答", "objective": True, "keys": ["临界", "幂律", "沙堆"], "source": "考古-复杂系统"},
    {"q": "什么是标度律？", "cat": "知识问答", "objective": True, "keys": ["幂律", "标度"], "source": "考古-复杂系统"},
    # 信号处理（批次1）
    {"q": "什么是傅里叶变换？", "cat": "知识问答", "objective": True, "keys": ["傅里叶", "频率", "分解"], "source": "考古-信号"},
    {"q": "什么是小波变换？", "cat": "知识问答", "objective": True, "keys": ["小波", "时频", "窗口"], "source": "考古-信号"},
    # 认知科学（批次2/3）
    {"q": "什么是工作记忆？", "cat": "知识问答", "objective": True, "keys": ["工作记忆", "容量", "暂时"], "source": "考古-认知"},
    {"q": "什么是认知偏差？", "cat": "知识问答", "objective": True, "keys": ["认知偏差", "确认偏差", "锚定"], "source": "考古-认知"},
    {"q": "什么是元认知？", "cat": "知识问答", "objective": True, "keys": ["元认知", "认知的认知", "监控"], "source": "考古-认知"},
    {"q": "什么是预测编码？", "cat": "知识问答", "objective": True, "keys": ["预测编码", "预测误差", "层级"], "source": "考古-认知"},
    {"q": "什么是内稳态？", "cat": "知识问答", "objective": True, "keys": ["内稳态", "负反馈", "稳定"], "source": "考古-认知"},
    # 数学（批次4）
    {"q": "什么是奇异值分解？", "cat": "知识问答", "objective": True, "keys": ["奇异值", "SVD", "分解"], "source": "考古-数学"},
    {"q": "什么是梯度下降？", "cat": "知识问答", "objective": True, "keys": ["梯度", "下降", "学习率"], "source": "考古-数学"},
    {"q": "什么是贝叶斯推断？", "cat": "知识问答", "objective": True, "keys": ["贝叶斯", "后验", "先验"], "source": "考古-数学"},
    {"q": "什么是凸优化？", "cat": "知识问答", "objective": True, "keys": ["凸", "优化", "全局最优"], "source": "考古-数学"},
    {"q": "什么是谱图论？", "cat": "知识问答", "objective": True, "keys": ["谱", "图", "特征值"], "source": "考古-数学"},
    {"q": "什么是VC维？", "cat": "知识问答", "objective": True, "keys": ["VC维", "打散", "复杂度"], "source": "考古-数学"},
    # ML（批次5）
    {"q": "什么是注意力机制？", "cat": "知识问答", "objective": True, "keys": ["注意力", "加权", "上下文"], "source": "考古-ML"},
    {"q": "什么是Transformer？", "cat": "知识问答", "objective": True, "keys": ["Transformer", "自注意力", "编码器"], "source": "考古-ML"},
    {"q": "什么是强化学习？", "cat": "知识问答", "objective": True, "keys": ["强化学习", "奖励", "策略"], "source": "考古-ML"},
    {"q": "什么是元学习？", "cat": "知识问答", "objective": True, "keys": ["元学习", "学会学习", "快速适应"], "source": "考古-ML"},
    {"q": "什么是神经缩放定律？", "cat": "知识问答", "objective": True, "keys": ["缩放定律", "幂律", "规模"], "source": "考古-ML"},
    # 博弈论（批次5）
    {"q": "什么是囚徒困境？", "cat": "知识问答", "objective": True, "keys": ["囚徒困境", "背叛", "合作"], "source": "考古-博弈"},
    {"q": "什么是纳什均衡？", "cat": "知识问答", "objective": True, "keys": ["纳什均衡", "最优策略"], "source": "考古-博弈"},
    {"q": "什么是效用理论？", "cat": "知识问答", "objective": True, "keys": ["效用", "偏好", "选择"], "source": "考古-博弈"},
]
print(f"考古 v2: {len(arch_v2)} 题")

# ===== 组装 v2 =====
v2 = []
for b in v2_blind:
    v2.append({"q": b["q"], "cat": "协议认知", "objective": True, "keys": [],
               "source": f"盲区-{b['kind']}-{b['blindspot_source']}"})
for r in v2_real:
    v2.append({"q": r["q"], "cat": r["cat"], "objective": r.get("objective", True),
               "keys": r.get("keys", []), "source": "真实对话弱命中"})
for a in arch_v2:
    v2.append(a)

seen = set()
dedup = []
for x in v2:
    if x["q"] in seen:
        continue
    seen.add(x["q"])
    dedup.append(x)

out = {"name": "new_testset_v2", "created": "2026-08-21",
       "sources": {"盲区": len(v2_blind), "真实对话弱命中": len(v2_real),
                   "考古新领域": len(arch_v2)},
       "items": dedup}
with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_v2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\n=== v2 组装完成: {len(dedup)} 题 ===")
print("来源分布:", out["sources"])

# 合并 v1+v2 → 全量
v1 = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_v1.json", encoding="utf-8"))["items"]
all_items = []
seen_all = set()
for x in v1 + dedup:
    if x["q"] in seen_all:
        continue
    seen_all.add(x["q"])
    all_items.append(x)
with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_full.json", "w", encoding="utf-8") as f:
    json.dump({"name": "new_testset_full", "created": "2026-08-21",
               "v1_count": len(v1), "v2_count": len(dedup),
               "total": len(all_items), "items": all_items},
              f, ensure_ascii=False, indent=1)
print(f"全量合并: {len(all_items)} 题（v1 {len(v1)} + v2 新增 {len(dedup)}）")
