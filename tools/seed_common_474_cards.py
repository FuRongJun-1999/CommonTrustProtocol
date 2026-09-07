# -*- coding: utf-8 -*-
"""seed_common_474_cards.py · 通识拓展批次474·存量卡补题（幂等）

474：3 张卡补 3 题（QB-1645~1647已用，本批QB-1657~1659）——
    科学巨匠三连：引力波 kp_card_gravitywave /
    牛顿第一定律 kp_card_newton1 / 元素周期表 kp_card_periodictable。
均已在库，无对应题（QB-1558 祖冲之圆周率、QB-1574 氧族、
QB-1602 光合实验均角度不同）。预检已过（QB-1657~1659 可用）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("QB-1657", "引力波是什么？LIGO 是怎么探测到引力波的？",
     "天文常识", "技术直答",
     ["引力波", "LIGO", "时空涟漪", "探测"], "通识拓展474·存量卡补题"),
    ("QB-1658", "牛顿第一定律的内容是什么？惯性是什么？",
     "物理基础", "技术直答",
     ["牛顿第一定律", "惯性", "静止", "匀速直线"], "通识拓展474·存量卡补题"),
    ("QB-1659", "元素周期表是谁发明的？它有什么规律和用途？",
     "化学基础", "技术直答",
     ["元素周期表", "门捷列夫", "原子序数", "周期性"], "通识拓展474·存量卡补题"),
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
    bank["version"] = "v7.43"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
