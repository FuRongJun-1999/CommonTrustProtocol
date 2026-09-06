# -*- coding: utf-8 -*-
"""seed_common_285_cards.py · 通识拓展批次285·存量卡补题·清单中部（幂等）

285：5 张卡补 5 题（QB-1078~1082）——史前夏商周/勒夏特列原理/汽化液化/
     郭沫若新诗/芳香烃
     清单索引1000起。预检已过（QB-1078~1082 可用）。
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
             "BCS"}


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
    ("QB-1078", "我国境内已知最早的人类是什么？河姆渡和半坡原始农耕有什么区别？",
     "历史", "学科直答",
     ["元谋人", "北京人", "河姆渡", "半坡"], "通识拓展285·存量卡补题"),
    ("QB-1079", "勒夏特列原理是什么？浓度温度压强怎么影响化学平衡？", "化学", "学科直答",
     ["平衡移动", "减弱", "浓度", "温度"], "通识拓展285·存量卡补题"),
    ("QB-1080", "蒸发和沸腾有什么区别？液化的两种方式是什么？", "物理", "学科直答",
     ["汽化", "液化", "蒸发", "沸腾"], "通识拓展285·存量卡补题"),
    ("QB-1081", "郭沫若《女神》在中国新诗史上有什么地位？代表作有哪些？",
     "语文", "学科直答",
     ["女神", "新诗", "奠基", "浪漫主义"], "通识拓展285·存量卡补题"),
    ("QB-1082", "芳香烃的结构特点是什么？甲苯能使高锰酸钾褪色吗？", "化学", "学科直答",
     ["苯环", "甲苯", "高锰酸钾", "褪色"], "通识拓展285·存量卡补题"),
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
    bank["version"] = "v5.56"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
