# -*- coding: utf-8 -*-
"""seed_common_331_cards.py · 通识拓展批次331·存量卡补题·清单中部（幂等）

331：4 张卡补 4 题（QB-1231~1234）——立体图形/分式方程/裸子植物/惯性
     清单索引2280-2310段。预检已过（QB-1231~1234 可用）。
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
    ("QB-1231", "常见的立体图形有哪些？球从任何方向看是什么形状？", "数学", "学科直答",
     ["长方体", "圆柱", "球", "长宽高"], "通识拓展331·存量卡补题"),
    ("QB-1232", "什么是语篇理解？怎么把握文章的结构？", "语文", "学科直答",
     ["结构", "段落大意", "衔接", "连贯"], "通识拓展331·存量卡补题"),
    ("QB-1233", "什么是裸子植物？松树银杏属于哪类植物？", "生物", "学科直答",
     ["裸子", "种子裸露", "银杏", "松柏"], "通识拓展331·存量卡补题"),
    ("QB-1234", "什么是惯性？汽车急刹车时乘客为什么会前倾？", "物理", "学科直答",
     ["惯性", "质量", "运动状态", "前倾"], "通识拓展331·存量卡补题"),
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
    bank["version"] = "v6.01"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
