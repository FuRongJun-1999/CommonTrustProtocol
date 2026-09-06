# -*- coding: utf-8 -*-
"""seed_common_307_cards.py · 通识拓展批次307·存量卡补题·清单中部（幂等）

307：5 张卡补 5 题（QB-1152~1156）——功/鸡兔同笼/中华文明起源/标点病句/
     当代世界
     清单索引2200起。预检已过（QB-1152~1156 可用）。
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
    ("QB-1152", "物理学中做功的两个必要因素是什么？功的单位是什么？", "物理", "学科直答",
     ["力", "距离", "焦耳", "做功"], "通识拓展307·存量卡补题"),
    ("QB-1153", "鸡兔同笼问题的经典解法是什么？", "数学", "学科直答",
     ["鸡兔同笼", "假设法", "腿", "头"], "通识拓展307·存量卡补题"),
    ("QB-1154", "中华文明「多元一体」是什么意思？", "历史", "学科直答",
     ["多元一体", "黄河", "长江", "夏商周"], "通识拓展307·存量卡补题"),
    ("QB-1155", "病句有哪些常见类型？怎么修改？", "语文", "学科直答",
     ["搭配不当", "成分残缺", "语序", "句式"], "通识拓展307·存量卡补题"),
    ("QB-1156", "当今世界的时代主题是什么？什么是人类命运共同体？", "政治", "学科直答",
     ["和平与发展", "多极化", "全球化", "命运共同体"], "通识拓展307·存量卡补题"),
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
    bank["version"] = "v5.77"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
