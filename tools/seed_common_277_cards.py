# -*- coding: utf-8 -*-
"""seed_common_277_cards.py · 通识拓展批次277·存量卡补题·清单中部（幂等）

277：4 张学术卡补 4 题（QB-1050~1053）——电负性/醇酚醚/功能关系/电解
     清单索引600起。预检已过（QB-1050~1053 可用）。
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
             "FADH2", "Vmax", "Km"}


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
    ("QB-1050", "电负性是什么？它在周期表中有什么变化规律？", "化学", "学科直答",
     ["电负性", "吸引电子", "同周期", "同主族"], "通识拓展277·存量卡补题"),
    ("QB-1051", "醇、酚、醚在结构上有什么区别？苯酚为什么显弱酸性？", "化学", "学科直答",
     ["羟基", "苯环", "苯酚", "弱酸性"], "通识拓展277·存量卡补题"),
    ("QB-1052", "功和能量之间是什么关系？动能定理怎么表述？", "物理", "学科直答",
     ["功", "能量", "转化", "动能定理"], "通识拓展277·存量卡补题"),
    ("QB-1053", "电解池的阴阳极各发生什么反应？电解是能量怎么转化的？", "化学", "学科直答",
     ["电解", "阳极", "氧化", "阴极"], "通识拓展277·存量卡补题"),
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.48"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
