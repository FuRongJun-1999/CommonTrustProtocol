# -*- coding: utf-8 -*-
"""seed_common_436_cards.py · 通识拓展批次436·存量卡补题（幂等）

436：3 张卡补 3 题（QB-1537~1539已用，本批QB-1546~1548）——
    生命科学三连：DNA与基因 kp_card_gene_dna / 人体免疫系统
    kp_card_immune / 达尔文与自然选择 kp_card_darwin。
均已在库，无对应题（题干角度与已有蛀牙/疫苗题区分）。
预检已过（QB-1546~1548 可用，三主题精确关键词 0 覆盖）。
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
    ("QB-1546", "DNA 和基因是什么关系？人类有多少条染色体？",
     "自然与生物", "技术直答",
     ["DNA", "基因", "染色体", "双螺旋"], "通识拓展436·存量卡补题"),
    ("QB-1547", "人体的三道免疫防线是什么？抗体是怎么工作的？",
     "健康与身体", "技术直答",
     ["免疫系统", "三道防线", "抗体", "疫苗"], "通识拓展436·存量卡补题"),
    ("QB-1548", "自然选择学说的核心内容是什么？达尔文的《物种起源》讲了什么？",
     "自然与生物", "技术直答",
     ["自然选择", "达尔文", "物种起源", "适者生存"], "通识拓展436·存量卡补题"),
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
    bank["version"] = "v7.07"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
