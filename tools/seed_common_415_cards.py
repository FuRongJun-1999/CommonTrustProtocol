# -*- coding: utf-8 -*-
"""seed_common_415_cards.py · 通识拓展批次415·存量卡补题（幂等）

415：3 张卡补 3 题（QB-1483~1485）——语言文字三连：
    成语的结构与文化 kp_card_chengyu（歇后语相关汉语知识角度，
    卡含成语来源四类）/ 世界主要语系 kp_card_langfamily /
    汉字的造字法六书 kp_card_charmake。均已在库，无题。
预检已过（QB-1483~1485 可用，三主题精确关键词 0 覆盖）。
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
    ("QB-1483", "成语主要有哪些来源？为什么说学成语要学它的典故？",
     "语文学习", "技术直答",
     ["成语", "来源", "典故", "四字"], "通识拓展415·存量卡补题"),
    ("QB-1484", "什么是语系？汉语属于哪个语系？",
     "语言常识", "技术直答",
     ["语系", "汉藏", "印欧", "汉语"], "通识拓展415·存量卡补题"),
    ("QB-1485", "汉字的造字法有哪几种？形声字和会意字怎么区分？",
     "语文学习", "技术直答",
     ["造字法", "六书", "象形", "形声"], "通识拓展415·存量卡补题"),
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
    bank["version"] = "v6.86"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
