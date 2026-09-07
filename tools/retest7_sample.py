# -*- coding: utf-8 -*-
"""retest7_sample.py · 第7次随机复测锚定：随机抽20题（固定种子）逐题验证。"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

BANK = os.path.join(HERE, "question_bank.json")


def main():
    from wisdom_book import ConditionDex
    from semantic_translate import card_route
    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    # 老题锚定：排除最近五批新增，验证早期入库知识的稳定性
    recent = {q["id"] for q in qs if q.get("source", "").startswith(("通识拓展40",))}
    pool = [q for q in qs if q["id"] not in recent]
    random.seed(20260907)
    sample = random.sample(pool, 20)
    dex = ConditionDex(db_path=os.path.join(ROOT, "aeis", "wisdom",
                                            "wisdom-book-cloud.db"))
    print("== 第7次随机复测锚定（种子20260907，池%d题抽20）==" % len(pool))
    hits = []
    for q in sample:
        r = card_route(dex, q["question"])
        top = max((c.get("score") or 0) for c in r) if r else 0
        ok = top >= 3
        hits.append(ok)
        print("%s | top=%.1f | %s | %s" % (
            q["id"], top, "PASS" if ok else "MISS", q["question"][:40]))
    print("--")
    print("结果: %d/20 满分, 缺口 %d" % (sum(hits), 20 - sum(hits)))
    return 0 if sum(hits) == 20 else 1


if __name__ == "__main__":
    sys.exit(main())
