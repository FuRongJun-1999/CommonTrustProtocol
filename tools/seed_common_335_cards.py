# -*- coding: utf-8 -*-
"""seed_common_335_cards.py · 通识拓展批次335·存量卡补题·清单中部（幂等）

335：4 张卡补 4 题（QB-1243~1246）——瑞利散射/师生关系/论述类文本/
     直线与圆位置关系
     清单索引2310-2350段。预检已过（QB-1243~1246 可用）。
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
    ("QB-1243", "天空为什么是蓝色的？晚霞为什么是红色的？", "物理", "学科直答",
     ["瑞利散射", "波长", "蓝光", "晚霞"], "通识拓展335·存量卡补题"),
    ("QB-1244", "好的师生关系是什么样的？怎么对待老师的批评？", "生活咨询", "情感陪伴",
     ["尊重", "勤学好问", "批评", "教学相长"], "通识拓展335·存量卡补题"),
    ("QB-1245", "论述类文本阅读要把握什么？论证方法有哪些？", "语文", "学科直答",
     ["论点", "论据", "论证", "思路"], "通识拓展335·存量卡补题"),
    ("QB-1246", "直线与圆有哪几种位置关系？怎么判断？", "数学", "学科直答",
     ["相交", "相切", "相离", "距离"], "通识拓展335·存量卡补题"),
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
    bank["version"] = "v6.05"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
