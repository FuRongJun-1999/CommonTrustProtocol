# -*- coding: utf-8 -*-
"""seed_common_301_cards.py · 通识拓展批次301·存量卡补题·清单中部（幂等）

301：5 张卡补 5 题（QB-1132~1136）——新中国成立/函数零点/等高线地形图/
     实用类文本/借用（Rust）
     清单索引1900起。预检已过（QB-1132~1136 可用）。
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
    ("QB-1132", "新中国成立是哪一年？建国初期的三大改造是什么？", "历史", "学科直答",
     ["1949", "开国大典", "三大改造", "一五计划"], "通识拓展301·存量卡补题"),
    ("QB-1133", "函数的零点是什么？零点存在定理的条件是什么？", "数学", "学科直答",
     ["零点", "交点", "异号", "存在定理"], "通识拓展301·存量卡补题"),
    ("QB-1134", "等高线地形图上怎么判断坡度陡缓？山峰山谷怎么区分？", "地理学", "学科直答",
     ["等高线", "密集", "陡", "山脊"], "通识拓展301·存量卡补题"),
    ("QB-1135", "实用类文本包括哪些类型？阅读实用文的关键是什么？", "语文", "学科直答",
     ["新闻", "传记", "科普", "信息获取"], "通识拓展301·存量卡补题"),
    ("QB-1136", "Rust 的借用规则是什么？为什么能在编译期防止数据竞争？",
     "编程", "学科直答",
     ["借用", "可变", "不可变", "编译期"], "通识拓展301·存量卡补题"),
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
    bank["version"] = "v5.71"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
