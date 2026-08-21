# -*- coding: utf-8 -*-
"""第二轮扩题：盲区模板剩余 + 数学/算法/信息论深概念（批次7 未覆盖）。

从 active_blindspot_report 剩余 + 图谱宽泛卡里挑「可能 llm 兜底」的题，
扩到 ~240 题，跑基线找真盲区。
"""
import json, sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")

# ===== 盲区剩余模板（数学/线代/算法/OS 深概念） =====
blind = json.load(open(r"D:\Program Files\2_ai\CommonTrustProtocol\tools\newset_blindspot_source.json", encoding="utf-8"))
used = {"科学方法论在什么条件下成立？", "智能论在什么条件下成立？",
        "二阶常系数线性方程在什么条件下成立？", "什么是智能论？", "什么是核与像？",
        "相似对角化的原理是什么？", "极限运算法则在什么条件下成立？",
        "方向导数与梯度在什么条件下成立？", "回溯与分支限界的原理是什么？"}
tmpl_v3 = []
for b in blind:
    q = b["q"]
    if q in used or q.endswith("在什么条件下成立？") and len(tmpl_v3) >= 15:
        continue
    if not q.endswith("在什么条件下成立？"):
        continue
    tmpl_v3.append({"q": q, "kind": "条件", "dnorm": b["dnorm"],
                    "source": "盲区-条件-BS-QUERY-WEAK"})
print(f"盲区模板 v3: {len(tmpl_v3)}")
for t in tmpl_v3:
    print(f"  {t['q']}")

# 非模板剩余（前 15 未用）
used2 = {"什么是政治学？", "什么是存在论？", "什么是统计学？", "什么是历史学？",
         "什么是进程线程？", "什么是环公理？", "伽罗瓦理论初步的原理是什么？",
         "施密特正交化的原理是什么？", "最大公因式的原理是什么？",
         "线性空间定义的原理是什么？", "最小多项式的原理是什么？",
         "双线性函数的原理是什么？", "连续与间断的原理是什么？",
         "单调性与极值的原理是什么？", "计算复杂性的原理是什么？",
         "系统调用中断的原理是什么？", "冯诺依曼体系是怎么工作的？",
         "不变子空间的原理是什么？", "I/O系统的原理是什么？",
         "价值理论与AI对齐的原理是什么？"}
nt_v3 = []
for b in blind:
    if b["q"] in used2 or b["q"].endswith("在什么条件下成立？"):
        continue
    nt_v3.append({"q": b["q"], "kind": b["kind"], "dnorm": b["dnorm"],
                  "source": f"盲区-{b['kind']}-{b['blindspot_source']}"})
print(f"\n盲区非模板 v3: {len(nt_v3)}")
for t in nt_v3[:15]:
    print(f"  [{t['dnorm']}] {t['q']}")

out = {"items": tmpl_v3[:15] + nt_v3[:15]}
with open(r"D:\Program Files\2_ai\knowledge-base\new_testset_v3_blind.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"\nv3 盲区草稿: {len(out['items'])} 题")
