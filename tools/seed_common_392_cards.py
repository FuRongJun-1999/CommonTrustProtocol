# -*- coding: utf-8 -*-
"""seed_common_392_cards.py · 通识拓展批次392·存量卡补题（幂等）

392：3 张卡补 3 题（QB-1414~1416）——软件质量/史前与夏商周/宏观经济学概述
     清单索引900与1000段取卡（垄断寡头/基尔霍夫/超导候选查重已有题
     被排除；饮食健康为英语话题卡跳过）。预检已过（QB-1414~1416 可用）。
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
    ("QB-1414", "软件质量有哪些关键属性？怎么保障软件质量？",
     "软件工程", "技术直答",
     ["软件质量", "可靠性", "测试", "评审"], "通识拓展392·存量卡补题"),
    ("QB-1415", "我国境内已知最早的人类是什么？夏商周各有什么文明标志？",
     "历史常识", "技术直答",
     ["元谋人", "北京人", "夏商周", "甲骨文"], "通识拓展392·存量卡补题"),
    ("QB-1416", "宏观经济学研究什么？宏观经济政策的目标有哪些？",
     "经济学常识", "技术直答",
     ["宏观经济", "总产出", "就业", "物价"], "通识拓展392·存量卡补题"),
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
    bank["version"] = "v6.62"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
