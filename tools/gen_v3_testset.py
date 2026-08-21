# -*- coding: utf-8 -*-
"""第三轮：新测试集 v3 组装（盲区 30 + 宽泛卡探测 50 + 考古补充），
合并 v1+v2 → 全量 ~250 题。"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

v3_blind = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_v3_blind.json", encoding="utf-8"))["items"]

# 宽泛卡探测的 50 题（都答对了，入新测试集作为回归基线）
probes = json.load(open(r"D:\Program Files\2_ai\knowledge-base\rebuild_probe_results.json", encoding="utf-8"))
probe_items = []
for p in probes:
    probe_items.append({"q": p["q"], "cat": "知识问答", "objective": True,
                        "keys": [], "source": f"宽泛卡-{p['card']}"})

# 考古批次1-5 补充子概念（v2 未覆盖的）
arch_v3 = [
    {"q": "什么是李雅普诺夫稳定性？", "cat": "知识问答", "objective": True, "keys": ["李雅普诺夫", "稳定"], "source": "考古-动态系统"},
    {"q": "什么是分岔理论？", "cat": "知识问答", "objective": True, "keys": ["分岔", "相变"], "source": "考古-动态系统"},
    {"q": "什么是Kuramoto模型？", "cat": "知识问答", "objective": True, "keys": ["Kuramoto", "相位同步", "耦合"], "source": "考古-同步"},
    {"q": "什么是功率谱密度？", "cat": "知识问答", "objective": True, "keys": ["功率谱", "频域"], "source": "考古-信号"},
    {"q": "什么是自适应滤波？", "cat": "知识问答", "objective": True, "keys": ["自适应", "滤波", "LMS"], "source": "考古-信号"},
    {"q": "什么是预测编码？", "cat": "知识问答", "objective": True, "keys": ["预测", "误差"], "source": "考古-认知"},
    {"q": "什么是STDP？", "cat": "知识问答", "objective": True, "keys": ["STDP", "时序", "可塑性"], "source": "考古-神经"},
    {"q": "什么是神经振荡？", "cat": "知识问答", "objective": True, "keys": ["振荡", "节律", "脑波"], "source": "考古-神经"},
    {"q": "什么是自由能原理？", "cat": "知识问答", "objective": True, "keys": ["自由能", "预测"], "source": "考古-认知"},
    {"q": "什么是二阶控制论？", "cat": "知识问答", "objective": True, "keys": ["二阶", "控制论", "观察者"], "source": "考古-控制论"},
    {"q": "什么是PID控制？", "cat": "知识问答", "objective": True, "keys": ["PID", "比例积分微分", "反馈"], "source": "考古-控制"},
    {"q": "什么是蒙特卡洛方法？", "cat": "知识问答", "objective": True, "keys": ["蒙特卡洛", "采样"], "source": "考古-数学"},
    {"q": "什么是不动点定理？", "cat": "知识问答", "objective": True, "keys": ["不动点", "压缩映射"], "source": "考古-数学"},
    {"q": "什么是偏差方差权衡？", "cat": "知识问答", "objective": True, "keys": ["偏差", "方差", "过拟合"], "source": "考古-ML"},
    {"q": "什么是正则化？", "cat": "知识问答", "objective": True, "keys": ["正则化", "L1", "L2"], "source": "考古-ML"},
    {"q": "什么是PAC学习？", "cat": "知识问答", "objective": True, "keys": ["PAC", "可能近似正确", "样本复杂度"], "source": "考古-ML"},
    {"q": "什么是扩散模型？", "cat": "知识问答", "objective": True, "keys": ["扩散", "去噪", "生成"], "source": "考古-ML"},
    {"q": "什么是对抗鲁棒性？", "cat": "知识问答", "objective": True, "keys": ["对抗", "鲁棒", "攻击"], "source": "考古-ML"},
    {"q": "什么是机制设计？", "cat": "知识问答", "objective": True, "keys": ["机制设计", "激励", "博弈"], "source": "考古-博弈"},
    {"q": "什么是贝叶斯决策？", "cat": "知识问答", "objective": True, "keys": ["贝叶斯", "决策", "期望效用"], "source": "考古-博弈"},
    {"q": "什么是合作博弈？", "cat": "知识问答", "objective": True, "keys": ["合作博弈", "联盟", "分配"], "source": "考古-博弈"},
    {"q": "什么是复制子方程？", "cat": "知识问答", "objective": True, "keys": ["复制子", "演化", "适应度"], "source": "考古-演化"},
    {"q": "什么是模因论？", "cat": "知识问答", "objective": True, "keys": ["模因", "文化", "传播"], "source": "考古-演化"},
    {"q": "什么是适应度景观？", "cat": "知识问答", "objective": True, "keys": ["适应度", "景观", "峰"], "source": "考古-演化"},
    {"q": "什么是信息瓶颈？", "cat": "知识问答", "objective": True, "keys": ["信息瓶颈", "互信息"], "source": "考古-信息论"},
    {"q": "什么是Kolmogorov复杂度？", "cat": "知识问答", "objective": True, "keys": ["Kolmogorov", "最短程序"], "source": "考古-信息论"},
]

# 组装 v3
v3 = []
for b in v3_blind:
    v3.append({"q": b["q"], "cat": "协议认知", "objective": True, "keys": [],
               "source": b["source"]})
for p in probe_items:
    v3.append(p)
for a in arch_v3:
    v3.append(a)

seen = set()
dedup = []
for x in v3:
    if x["q"] in seen:
        continue
    seen.add(x["q"])
    dedup.append(x)

with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_v3.json", "w", encoding="utf-8") as f:
    json.dump({"name": "new_testset_v3", "sources": {"盲区": len(v3_blind),
               "宽泛卡探测": len(probe_items), "考古": len(arch_v3)},
               "items": dedup}, f, ensure_ascii=False, indent=1)
print(f"v3: {len(dedup)} 题（盲区 {len(v3_blind)} + 宽泛卡 {len(probe_items)} + 考古 {len(arch_v3)}）")

# 合并全部
all_items = []
seen_all = set()
for name in ("new_testset_full.json", "new_testset_v3.json"):
    d = json.load(open(rf"D:\Program Files\2_ai\knowledge-base\{name}", encoding="utf-8"))
    items = d.get("items", d if isinstance(d, list) else [])
    for x in items:
        if x["q"] in seen_all:
            continue
        seen_all.add(x["q"])
        all_items.append(x)
with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_master.json", "w", encoding="utf-8") as f:
    json.dump({"name": "new_testset_master", "total": len(all_items),
               "items": all_items}, f, ensure_ascii=False, indent=1)
print(f"master 全量: {len(all_items)} 题")
