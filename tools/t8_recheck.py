# -*- coding: utf-8 -*-
"""t8_recheck.py · 主仓库迁移后白箱直答复查（2026-08-30 荣指令）

对照 T8 直答质量抽查表（24 题，2026-08-29 人工评定 83-88%）：
- 回答率：card_route 命中且返回直答的题数 / 24
- key_hit：直答全文含参考答案关键词（自动口径，仅供参考）
- 人工判定：输出全部直答供人工标 ✓/✗（正确/错误）
"""
import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

from wisdom_book import ConditionDex
from semantic_translate import card_route

DEX = ConditionDex(db_path=os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db"),
                   fresh=False)

# ---- 解析 24 题（T8 抽查表）----
md = open(os.path.join(ROOT, "docs", "T8直答质量抽查表.md"), encoding="utf-8").read()
questions = []
for line in md.splitlines():
    m = re.match(r"\| (\d+) \| (.+?) \|", line)
    if m:
        questions.append((int(m.group(1)), m.group(2).strip()))
questions.sort()
print(f"解析到 {len(questions)} 题")

# ---- 参考答案关键词（人工判定依据）----
KEYWORDS = {
    1: ["180"],
    2: ["反射角等于入射角", "法线"],
    3: ["换元", "变量替换"],
    4: ["氢", "氧"],
    5: ["细胞分裂", "一个细胞分成两个"],
    6: ["鸦片战争", "1840"],
    7: ["SYN", "三次握手"],
    8: ["度分布", "频率"],
    9: ["插入排序", "有序"],
    10: ["工作窃取", "队列"],
    11: ["TCP", "UDP", "连接"],
    12: ["就绪队列", "调度"],
    13: ["丈夫", "边界"],
    14: ["止损", "盘点"],
    15: ["育儿", "冲突"],
    16: ["宠物", "日程"],
    17: ["拖延", "精力"],
    18: ["租金", "30%"],
    19: ["结论先行"],
    20: ["编程语言", "入门"],
    21: ["复合赋值"],
    22: ["str", "upper"],
    23: ["print", "多参数"],
    24: ["圈量子", "广义相对论"],
}

# ---- 直答评测（M1.2 门槛：MIN_ACCEPT_SCORE=5）----
MIN_SCORE = 5
results = []
hit = miss = 0
for num, q in questions:
    try:
        hs = card_route(DEX, q, limit=1)
        if hs and hs[0].get("score", 0) >= MIN_SCORE:
            card = hs[0]
            # 直答全文 = direct_answer 字段（T8 口径）
            answer = str(card.get("direct_answer") or card.get("name") or card)[:300]
            hit += 1
        else:
            answer = "（BLINDSPOT：无达标命中）"
            miss += 1
    except Exception as e:
        answer = f"（异常: {e}）"
        miss += 1
    # 自动 key_hit（关键词包含）
    kws = KEYWORDS.get(num, [])
    hit_kw = sum(1 for k in kws if k in answer)
    key_ok = hit_kw >= 1 if kws else None
    results.append((num, q, answer, key_ok))

print(f"\n==== 白箱直答复查（主仓库迁移后）====")
print(f"回答率: {hit}/{len(questions)} = {hit/len(questions)*100:.1f}%")
auto_ok = sum(1 for r in results if r[3] is True)
print(f"自动 key_hit 通过: {auto_ok}/{len(questions)}（口径仅供参考）")
print()
print("| # | 问题 | 直答（截断80字） | key_hit |")
for num, q, ans, key_ok in results:
    a = ans[:80].replace("|", "/").replace("\n", " ")
    k = "✓" if key_ok else ("✗" if key_ok is not None else "-")
    print(f"| {num} | {q[:20]} | {a} | {k} |")

# 未命中清单
print("\n==== 未命中（回答率缺口）====")
for num, q, ans, _ in results:
    if ans.startswith("（BLINDSPOT") or ans.startswith("（异常"):
        print(f"  #{num} {q}")
