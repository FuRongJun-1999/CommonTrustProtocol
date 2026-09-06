# -*- coding: utf-8 -*-
"""seed_common_319_cards.py · 通识拓展批次319·存量卡补题·清单中部（幂等）

319：4 张卡补 4 题（QB-1195~1198）——时评写作/用字母表示数/宋元时期/看图写话
     清单索引2200后段。预检已过（QB-1195~1198 可用）。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("QB-1195", "时评写作有什么要求？怎么写好一篇时事评论？", "语文", "学科直答",
     ["时评", "观点", "有理有据", "思辨"], "通识拓展319·存量卡补题"),
    ("QB-1196", "用字母表示数有什么好处？什么是代数思维？", "数学", "学科直答",
     ["字母", "表示数", "式子", "任意"], "通识拓展319·存量卡补题"),
    ("QB-1197", "宋元时期有哪些重要发明和经济成就？行省制是什么？", "历史", "学科直答",
     ["交子", "岳飞", "行省制", "四大发明"], "通识拓展319·存量卡补题"),
    ("QB-1198", "看图写话有什么方法？怎么把图上的内容写清楚？", "语文", "学科直答",
     ["观察", "顺序", "谁", "做什么"], "通识拓展319·存量卡补题"),
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
    bank["version"] = "v5.89"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
