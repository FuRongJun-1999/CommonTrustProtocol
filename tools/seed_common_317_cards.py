# -*- coding: utf-8 -*-
"""seed_common_317_cards.py · 通识拓展批次317·存量卡补题（幂等）

317：4 张卡补 4 题（QB-1189~1192）——新时期文学/FPGA可编程逻辑/
     NoSQL数据库/常见连续分布
     全库回扫候选。预检已过（QB-1189~1192 可用）。
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
             "BCS", "B2H6", "borrow", "Rust", "NoSQL", "Redis", "MongoDB",
             "FPGA", "PLA", "PAL", "GAL", "CPLD", "PLD"}


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
    ("QB-1189", "新时期文学（1978 年后）有哪些思潮？伤痕文学是什么？", "语文", "学科直答",
     ["伤痕文学", "反思", "寻根", "新时期"], "通识拓展317·存量卡补题"),
    ("QB-1190", "FPGA 是什么？它和普通芯片有什么区别？", "编程", "学科直答",
     ["FPGA", "可编程", "硬件", "重构"], "通识拓展317·存量卡补题"),
    ("QB-1191", "NoSQL 数据库有哪些类型？和关系数据库有什么区别？", "编程", "学科直答",
     ["NoSQL", "键值", "文档", "关系"], "通识拓展317·存量卡补题"),
    ("QB-1192", "均匀分布和指数分布各是什么？指数分布的「无记忆性」指什么？",
     "数学", "学科直答",
     ["均匀分布", "指数分布", "无记忆", "密度"], "通识拓展317·存量卡补题"),
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
    bank["version"] = "v5.87"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
