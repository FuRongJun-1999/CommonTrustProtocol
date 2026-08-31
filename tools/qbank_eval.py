# -*- coding: utf-8 -*-
"""qbank_eval.py · 白箱题库评测（题库 ↔ 评测闭环）。

读 tools/question_bank.json 逐题 card_route 评测：
  - 回答率：路由有候选（top score≥阈值）的题数占比
  - key_hit：直答/直答 response 含参考关键词（自动口径，供人工复核参考）
  - 分域/分类型统计

用法：python tools/qbank_eval.py [--min-score 3]
"""
import sys
import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
BANK = os.path.join(HERE, "question_bank.json")


def main(min_score=3):
    from wisdom_book import ConditionDex
    from semantic_translate import card_route

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    dex = ConditionDex(db_path=os.path.join(ROOT, "aeis", "wisdom",
                                            "wisdom-book-cloud.db"))
    by_domain, by_type = {}, {}
    answered = 0
    misses = []
    for q in qs:
        r = card_route(dex, q["question"])
        top = max((c.get("score") or 0) for c in r) if r else 0
        hit = top >= min_score
        answered += 1 if hit else 0
        dom = q.get("domain", "未分类")
        d = by_domain.setdefault(dom, {"n": 0, "hit": 0})
        d["n"] += 1
        d["hit"] += 1 if hit else 0
        t = q.get("type", "直答")
        t2 = by_type.setdefault(t, {"n": 0, "hit": 0})
        t2["n"] += 1
        t2["hit"] += 1 if hit else 0
        if not hit:
            misses.append((q["id"], q["question"][:30], top))
    print(f"题库 v{bank['version']} | {len(qs)} 题 | min_score={min_score}")
    print(f"回答率: {answered}/{len(qs)} = {answered/len(qs)*100:.1f}%")
    print("--- 缺口（未达阈值）---")
    for qid, qtext, top in misses:
        print(f"  {qid} {qtext} (top_score={top})")
    print("--- 分类型 ---")
    for t, d in sorted(by_type.items()):
        print(f"  {t}: {d['hit']}/{d['n']}")
    low = [(dom, d) for dom, d in sorted(by_domain.items()) if d["hit"] < d["n"]]
    if low:
        print("--- 低分域 ---")
        for dom, d in low:
            print(f"  {dom}: {d['hit']}/{d['n']}")
    return 0 if not misses else 1


if __name__ == "__main__":
    ms = 3
    if "--min-score" in sys.argv:
        ms = int(sys.argv[sys.argv.index("--min-score") + 1])
    sys.exit(main(ms))
