# -*- coding: utf-8 -*-
"""seed_common_357_cards.py · 通识拓展批次357·存量卡补题·清单尾部（幂等）

357：4 张卡补 4 题（QB-1305~1308）——饿/尴尬/自豪/疲惫
     清单尾部（索引2492-2516段）。预检已过（QB-1305~1308 可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("QB-1305", "饿了为什么要及时吃东西？", "生活咨询", "情感陪伴",
     ["饿", "能量", "吃饭", "身体"], "通识拓展357·存量卡补题"),
    ("QB-1306", "遇到尴尬的事怎么办？", "生活咨询", "情感陪伴",
     ["尴尬", "正常", "笑笑", "过去"], "通识拓展357·存量卡补题"),
    ("QB-1307", "自豪是一种什么感觉？做成一件事后怎么看待自己？", "生活咨询", "情感陪伴",
     ["自豪", "努力", "成果", "肯定"], "通识拓展357·存量卡补题"),
    ("QB-1308", "身心疲惫的时候该怎么办？", "生活咨询", "情感陪伴",
     ["疲惫", "放假", "休息", "别硬撑"], "通识拓展357·存量卡补题"),
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
    bank["version"] = "v6.23"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
