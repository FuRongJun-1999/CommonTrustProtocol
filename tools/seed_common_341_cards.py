# -*- coding: utf-8 -*-
"""seed_common_341_cards.py · 通识拓展批次341·存量卡补题·清单中部（幂等）

341：4 张卡补 4 题（QB-1261~1264）——名句默写/幂函数/平移/圆
     清单索引2395-2441段。预检已过（QB-1261~1264 可用）。
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
    ("QB-1261", "名句默写怎么避免错别字？理解记忆和死记硬背哪个好？", "语文", "学科直答",
     ["默写", "错别字", "理解", "积累"], "通识拓展341·存量卡补题"),
    ("QB-1262", "幂函数是什么形式？图像性质由什么决定？", "数学", "学科直答",
     ["幂函数", "指数", "第一象限", "图像"], "通识拓展341·存量卡补题"),
    ("QB-1263", "什么是平移？平移后的图形和原图形有什么关系？", "数学", "学科直答",
     ["平移", "全等", "方向", "距离"], "通识拓展341·存量卡补题"),
    ("QB-1264", "圆有什么基本性质？直径和半径是什么关系？", "数学", "学科直答",
     ["圆", "圆心", "半径", "直径"], "通识拓展341·存量卡补题"),
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
    bank["version"] = "v6.10"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
