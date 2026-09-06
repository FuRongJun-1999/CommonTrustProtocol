# -*- coding: utf-8 -*-
"""seed_common_323_cards.py · 通识拓展批次323·存量卡补题·清单中部（幂等）

323：4 张卡补 4 题（QB-1207~1210）——创新意识/电功率/有理数/弧度制
     清单索引2350起。预检已过（QB-1207~1210 可用）。
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
             "BCS", "B2H6", "borrow", "Rust", "Dijkstra", "Bellman",
             "Floyd", "logV", "sin", "cos", "tan"}


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
    ("QB-1207", "什么是创新意识？一题多解对培养创新有什么帮助？", "数学", "学科直答",
     ["创新", "角度", "一题多解", "方法"], "通识拓展323·存量卡补题"),
    ("QB-1208", "电功率表示什么？额定功率和实际功率有什么区别？", "物理", "学科直答",
     ["电功率", "电压", "电流", "瓦特"], "通识拓展323·存量卡补题"),
    ("QB-1209", "什么是有理数？数轴上数的大小怎么比较？", "数学", "学科直答",
     ["有理数", "整数", "分数", "数轴"], "通识拓展323·存量卡补题"),
    ("QB-1210", "什么是弧度制？弧度和角度怎么换算？", "数学", "学科直答",
     ["弧度", "半径", "π", "180"], "通识拓展323·存量卡补题"),
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
    bank["version"] = "v5.93"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
