# -*- coding: utf-8 -*-
"""seed_common_441_cards.py · 通识拓展批次441·存量卡补题（幂等）

441：3 张卡补 3 题（QB-1561~1563）——身体奥秘三连：
    ABO血型与输血原则 kp_card_bloodtype / 耳与听觉的形成
    kp_card_earhear / 微量元素与人体健康 kp_card_traceelem。
均已在库，无对应题。预检已过（QB-1561~1563 可用，
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
    ("QB-1561", "ABO 血型分为哪四种？输血为什么要遵守同型原则？",
     "健康与身体", "技术直答",
     ["血型", "输血", "抗原", "熊猫血"], "通识拓展441·存量卡补题"),
    ("QB-1562", "耳朵的结构分为哪三部分？坐飞机时耳朵发闷是怎么回事？",
     "健康与身体", "技术直答",
     ["耳朵", "鼓膜", "耳蜗", "咽鼓管"], "通识拓展441·存量卡补题"),
    ("QB-1563", "人体必需的微量元素有哪些？缺铁、缺碘会得什么病？",
     "健康与身体", "技术直答",
     ["微量元素", "缺铁", "缺碘", "健康"], "通识拓展441·存量卡补题"),
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
    bank["version"] = "v7.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
