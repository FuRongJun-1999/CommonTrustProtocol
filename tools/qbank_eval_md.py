# -*- coding: utf-8 -*-
"""qbank_eval_md.py · 白箱题库评测（MD 目录后端）

与 qbank_eval.py 功能完全一致，但数据源从 sqlite 切换到 MD 目录：
  - 知识内容：aeis/knowledge/*.md（246 个学科综述）
  - 路由索引：aeis/knowledge/_ccg_dump.json（CCG 注释快照）
  - 检索引擎：card_route（评分逻辑与 sqlite 版完全一致）

用法：python tools/qbank_eval_md.py [--min-score 3]
"""
import sys, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
sys.path.insert(0, HERE)
BANK = os.path.join(HERE, "question_bank.json")
CCG_DUMP = os.path.join(ROOT, "aeis", "knowledge", "_ccg_dump.json")


def main(min_score=3):
    from semantic_translate import card_route
    from md_dex import MdConditionDex

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]

    dex = MdConditionDex(CCG_DUMP)
    print(f"MD 后端加载: {dex.row_count} 条路由记录")

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
