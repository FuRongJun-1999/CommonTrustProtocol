# -*- coding: utf-8 -*-
"""seed_common_337_cards.py · 通识拓展批次337·存量卡补题·清单中部（幂等）

337：4 张卡补 4 题（QB-1249~1252）——比值/诚实守信/离子/点线面体
     清单索引2370-2387段。预检已过（QB-1249~1252 可用）。
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
    ("QB-1249", "什么是比值？比值可以是什么形式的数？", "数学", "学科直答",
     ["比值", "前项", "后项", "商"], "通识拓展337·存量卡补题"),
    ("QB-1250", "诚实守信为什么重要？失信会有什么后果？", "政治", "学科直答",
     ["诚信", "立身", "信任", "失信"], "通识拓展337·存量卡补题"),
    ("QB-1251", "什么是离子？阳离子和阴离子有什么区别？", "化学", "学科直答",
     ["离子", "阳离子", "阴离子", "带电"], "通识拓展337·存量卡补题"),
    ("QB-1252", "点、线、面、体之间有什么关系？", "数学", "学科直答",
     ["点动成线", "线动成面", "面动成体", "基本元素"], "通识拓展337·存量卡补题"),
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
    bank["version"] = "v6.06"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
