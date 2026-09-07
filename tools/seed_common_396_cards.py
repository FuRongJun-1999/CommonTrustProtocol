# -*- coding: utf-8 -*-
"""seed_common_396_cards.py · 通识拓展批次396·存量卡补题（幂等）

396：3 张卡补 3 题（QB-1426~1428）——芳烃亲电取代/特征值问题/拉格朗日方程
     清单索引500段取卡（氢键候选查重已有 QB-1044、细胞化合物角度
     与 QB-229/422 近似被排除）。预检已过（QB-1426~1428 可用，
     三主题精确关键词 0 覆盖）。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


QUESTIONS = [
    ("QB-1426", "芳烃的亲电取代反应有哪些类型？取代基的定位效应是什么？",
     "有机化学", "技术直答",
     ["芳烃", "亲电取代", "定位效应", "硝化"], "通识拓展396·存量卡补题"),
    ("QB-1427", "什么是特征值问题？特征函数为什么重要？",
     "数学物理", "技术直答",
     ["特征值", "特征函数", "正交", "展开"], "通识拓展396·存量卡补题"),
    ("QB-1428", "拉格朗日方程是什么？它相比牛顿法有什么优势？",
     "理论力学", "技术直答",
     ["拉格朗日方程", "最小作用量", "约束", "力学"], "通识拓展396·存量卡补题"),
]


def ensure_seed() -> dict:
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = " ".join(q[1] + " " + " ".join(q[4]) for q in QUESTIONS)
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.66"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
