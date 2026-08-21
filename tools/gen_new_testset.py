# -*- coding: utf-8 -*-
"""新测试集组装（v1.26 · 持续学习流程第三步）

三来源组合：
  1. 盲区注册表（BS-QUERY-WEAK/BS-ACTIVE-PROBE 未解决盲区）→ 原理/条件/机制类
  2. 真实对话弱命中（v7 route=llm 但答对 = 白箱弱命中）→ 优先选知识类
  3. 知识考古新领域（批次6 工程数学 15 卡）→ 未覆盖子概念问题

输出：new_testset_*.json（含 q/cat/objective/keys/source）
"""
import json, sys, random
sys.stdout.reconfigure(encoding="utf-8")

random.seed(20260821)

# ===== 来源一：盲区 =====
blind = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\tools\newset_blindspot_source.json", encoding="utf-8"))
# 取 dnorm 最高、问题形式完整的（前 20，跳过太泛的「X在什么条件下成立」重复模板）
bs_sel = []
for b in blind:
    q = b["q"]
    # 跳过重复模板（大量「XX在什么条件下成立」——只取少量代表性的）
    if q.endswith("在什么条件下成立？") and len(bs_sel) >= 6:
        continue
    bs_sel.append(b)
    if len(bs_sel) >= 20:
        break
print(f"盲区来源: {len(bs_sel)} 题")
for b in bs_sel:
    print(f"  [{b['dnorm']}] {b['q']}")

# ===== 来源二：真实对话弱命中 =====
real = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\tools\newset_realdialogue_source.json", encoding="utf-8"))
# 优先知识类/条件判断/编程/协议认知（弱命中是知识缺口），剔除意见请求/闲聊
real_know = [r for r in real if r["cat"] in ("知识问答", "条件判断", "编程语言", "协议认知", "生活常识")]
print(f"\n真实对话弱命中(知识类): {len(real_know)} 题")
for r in real_know[:20]:
    print(f"  [{r['cat']}] {r['q']}")

# ===== 来源三：知识考古新领域（批次6 工程数学子概念） =====
arch = [
    # 复分析
    {"q": "什么是留数定理？", "cat": "知识问答", "objective": True, "keys": ["留数", "极点", "围道"], "source": "考古-复分析"},
    {"q": "共形映射是什么？", "cat": "知识问答", "objective": True, "keys": ["保角", "共形"], "source": "考古-复分析"},
    # 群论
    {"q": "什么是群？", "cat": "知识问答", "objective": True, "keys": ["封闭", "结合", "单位元", "逆元"], "source": "考古-群论"},
    {"q": "对称性和群有什么关系？", "cat": "知识问答", "objective": True, "keys": ["对称", "群"], "source": "考古-群论"},
    # SDE
    {"q": "什么是随机微分方程？", "cat": "知识问答", "objective": True, "keys": ["随机", "布朗运动", "伊藤"], "source": "考古-SDE"},
    {"q": "伊藤引理是什么？", "cat": "知识问答", "objective": True, "keys": ["伊藤", "随机"], "source": "考古-SDE"},
    # 生成函数
    {"q": "什么是生成函数？", "cat": "知识问答", "objective": True, "keys": ["幂级数", "生成函数"], "source": "考古-生成函数"},
    # FEM
    {"q": "有限元方法是什么？", "cat": "知识问答", "objective": True, "keys": ["离散", "有限单元", "刚度"], "source": "考古-FEM"},
    # 共轭梯度
    {"q": "共轭梯度法有什么用？", "cat": "知识问答", "objective": True, "keys": ["共轭方向", "迭代"], "source": "考古-共轭梯度"},
    # 张量分解
    {"q": "什么是张量分解？", "cat": "知识问答", "objective": True, "keys": ["CP分解", "Tucker", "低秩"], "source": "考古-张量"},
    # PGM
    {"q": "什么是概率图模型？", "cat": "知识问答", "objective": True, "keys": ["条件独立", "贝叶斯网络", "马尔可夫"], "source": "考古-PGM"},
    {"q": "贝叶斯网络和有向图什么关系？", "cat": "知识问答", "objective": True, "keys": ["贝叶斯网络", "有向"], "source": "考古-PGM"},
    # 高斯过程
    {"q": "什么是高斯过程？", "cat": "知识问答", "objective": True, "keys": ["高斯过程", "核函数", "协方差"], "source": "考古-GP"},
    # OT
    {"q": "什么是最优传输？", "cat": "知识问答", "objective": True, "keys": ["Wasserstein", "搬运", "最优传输"], "source": "考古-OT"},
    {"q": "Wasserstein距离是什么？", "cat": "知识问答", "objective": True, "keys": ["Wasserstein", "距离"], "source": "考古-OT"},
    # 微分几何
    {"q": "什么是流形？", "cat": "知识问答", "objective": True, "keys": ["流形", "局部", "欧几里得"], "source": "考古-微分几何"},
    # 数值线性代数
    {"q": "什么是条件数？", "cat": "知识问答", "objective": True, "keys": ["条件数", "数值稳定"], "source": "考古-数值线代"},
    {"q": "QR分解是什么？", "cat": "知识问答", "objective": True, "keys": ["QR", "正交"], "source": "考古-数值线代"},
    # STFT
    {"q": "短时傅里叶变换解决什么问题？", "cat": "知识问答", "objective": True, "keys": ["时频", "STFT", "窗口"], "source": "考古-STFT"},
    # 排队论
    {"q": "什么是利特尔法则？", "cat": "知识问答", "objective": True, "keys": ["利特尔", "L=λW"], "source": "考古-排队论"},
    # MCMC
    {"q": "蒙特卡洛方法是什么？", "cat": "知识问答", "objective": True, "keys": ["蒙特卡洛", "采样", "随机"], "source": "考古-MCMC"},
    {"q": "马尔可夫链蒙特卡洛是干什么的？", "cat": "知识问答", "objective": True, "keys": ["马尔可夫链", "平稳分布", "采样"], "source": "考古-MCMC"},
]
print(f"\n考古新领域: {len(arch)} 题")

# ===== 组装 =====
newset = []
for b in bs_sel:
    newset.append({"q": b["q"], "cat": "协议认知", "objective": True,
                   "keys": [], "source": f"盲区-{b['kind']}-{b['blindspot_source']}"})
for r in real_know[:30]:
    newset.append({"q": r["q"], "cat": r["cat"], "objective": r.get("objective", True),
                   "keys": r.get("keys", []), "source": "真实对话弱命中"})
for a in arch:
    newset.append(a)

# 去重（q 相同）
seen = set()
dedup = []
for x in newset:
    if x["q"] in seen:
        continue
    seen.add(x["q"])
    dedup.append(x)

out = {"name": "new_testset_v1", "created": "2026-08-21",
       "sources": {"盲区": len(bs_sel), "真实对话弱命中": min(len(real_know), 30),
                   "考古新领域": len(arch)},
       "items": dedup}
with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_v1.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\n=== 新测试集组装完成: {len(dedup)} 题 ===")
print("来源分布:", out["sources"])
