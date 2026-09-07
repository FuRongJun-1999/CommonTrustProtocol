# -*- coding: utf-8 -*-
"""seed_common_487_cards.py · 通识拓展批次487·存量卡补题（幂等）

487：3 张卡补 3 题（QB-1696~1698）——种群数量变化/微分方程应用/
    计算复杂性。清单索引240段取卡，三主题精确查重 0 覆盖。
预检已过（QB-1696~1698 可用）。
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
    ("QB-1696", "种群增长的 J 型和 S 型曲线有什么区别？什么是 K 值？",
     "自然与生物", "技术直答",
     ["种群", "J型", "S型", "K值"], "通识拓展487·存量卡补题"),
    ("QB-1697", "微分方程有哪些实际应用？什么是指数增长模型？",
     "数学应用", "技术直答",
     ["微分方程", "建模", "指数增长", "应用"], "通识拓展487·存量卡补题"),
    ("QB-1698", "什么是计算复杂性？P 问题和 NP 问题有什么区别？",
     "计算机科学", "技术直答",
     ["计算复杂性", "P问题", "NP问题", "多项式"], "通识拓展487·存量卡补题"),
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
    bank["version"] = "v7.53"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
