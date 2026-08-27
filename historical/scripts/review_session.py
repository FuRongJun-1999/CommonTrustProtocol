# -*- coding: utf-8 -*-
"""持续学习循环 2 小时复盘（v1.26 · 2026-08-21）

4 轮循环 → 统计成果。
"""
import json, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding="utf-8")

print("=" * 56)
print("持续学习循环 2 小时复盘")
print("=" * 56)

# master 全量
m = json.load(open(r"D:\Program Files\2_ai\knowledge-base\new_testset_master_results.json", encoding="utf-8"))
print(f"\n【新测试集 master】{m['total']} 题")
print(f"  总正确: {m['correct']}/{m['total']} ({m['rate']*100:.1f}%)")
print(f"  self 直答: {m['self_ok']}/{m['self_n']} ({m['self_ok']/m['self_n']*100:.1f}%)")
rc = Counter(x['route'] for x in m['results'])
print(f"  route: {dict(rc)}")
by_src = defaultdict(lambda: [0, 0])
for x in m['results']:
    s = x.get('source', '?').split('-')[0]
    by_src[s][0] += x['score']
    by_src[s][1] += 1
print("  按来源:")
for s, (c, n) in sorted(by_src.items(), key=lambda x: -x[1][0]/x[1][1]):
    print(f"    {s}: {c:.0f}/{n} ({c/n*100:.1f}%)")

# 错题复测
r = json.load(open(r"D:\Program Files\2_ai\knowledge-base\recognized_sets\dialogue_1000_v7_rerun_results.json", encoding="utf-8"))
print(f"\n【错题复测集】{r['n']} 题: {r['correct']:.0f}/{r['n']} ({r['correct']/r['n']*100:.0f}%)")

# 200 题回归
d200 = json.load(open(r"D:\Program Files\2_ai\knowledge-base\dialogue_200_results.json", encoding="utf-8"))
print(f"【200 题回归】{d200['correct']:.0f}/{d200['total']} ({d200['rate']*100:.1f}%)")

print("\n【补卡批次】")
print("  批次7: 13 概念（核与像/相似对角化/施密特正交化/行列式/极限运算法则/")
print("         方向导数与梯度/格林公式/多元极值/二阶常系数线性方程/回溯/分支限界/")
print("         科学方法论/智能论）")
print("  批次8: 8 概念（唐诗/免疫系统/放射性衰变/辩证法/能带/梁的弯曲/唯物史观/黑洞）")
print("  批次9: 2 概念（随机化算法/认知双过程）")
print("  批次10: 5 概念（色谱法/能级/混凝土/弹性/宋词）")

print("\n【修复根因】")
print("  1. 条件词防护误伤真空（声音传播）→ 瘦身防护")
print("  2. 群体比较无客观答案 → 新增 group_compare 诚实边界")
print("  3. 反向检查泛词过度触发（共轭梯度被方向导数抢答）→ 子串包含跳过")
print("  4. _dt 选择按触发短语长度（梯度下降被方向导数抢答）")
print("  5. _decide_route 只看 top hit → 遍历 strong 匹配")
print("  6. 智能论条件题 → 补条件卡+触发词")
print("  7. 吸管回归（大气压触发词缺变体）→ 补触发词")
print("  8. 沸点与气压卡无触发词 → 补簇+直答")
