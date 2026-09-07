# -*- coding: utf-8 -*-
"""seed_common_416_cards.py · 通识拓展批次416·存量卡补题（幂等）

416：3 张卡补 3 题（QB-1486~1488）——能源三连：能量守恒定律
    kp_card_energysave / 化石燃料 kp_card_fossilfuel /
    能源与可持续发展 kp_card_sustdev。均已在库。
（角度规避：永动机 QB-156、化石综合利用 QB-596、碳中和 QB-187/604。）
预检已过（QB-1486~1488 可用，三题精确角度 0 覆盖）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("QB-1486", "能量守恒定律说的是什么？能量的转移和转化有什么区别？",
     "物理基础", "技术直答",
     ["能量守恒", "定律", "转化", "转移"], "通识拓展416·存量卡补题"),
    ("QB-1487", "煤、石油、天然气是怎么形成的？为什么说它们不可再生？",
     "自然常识", "技术直答",
     ["化石燃料", "煤", "石油", "天然气"], "通识拓展416·存量卡补题"),
    ("QB-1488", "什么是碳达峰？氢能为什么被称为「终极能源」？",
     "自然常识", "技术直答",
     ["碳达峰", "氢能", "新能源", "可持续"], "通识拓展416·存量卡补题"),
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
    bank["version"] = "v6.87"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
