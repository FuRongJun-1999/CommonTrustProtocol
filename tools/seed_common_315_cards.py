# -*- coding: utf-8 -*-
"""seed_common_315_cards.py · 通识拓展批次315·存量卡补题·清单尾部（幂等）

315：4 张卡补 4 题（QB-1183~1186）——面向对象/异常处理/倾听共情/冷的照顾
     清单尾部（索引2523-2530）。预检已过（QB-1183~1186 可用）。
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
             "BCS", "B2H6", "borrow", "Rust", "try", "catch"}


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
    ("QB-1183", "面向对象编程的三大特性是什么？什么是封装？", "编程", "学科直答",
     ["封装", "继承", "多态", "类"], "通识拓展315·存量卡补题"),
    ("QB-1184", "程序异常处理是干什么的？try/catch 怎么工作？", "编程", "学科直答",
     ["异常", "捕获", "运行时", "恢复"], "通识拓展315·存量卡补题"),
    ("QB-1185", "家庭矛盾中怎么沟通？倾听共情有什么用？", "生活咨询", "情感陪伴",
     ["倾听", "共情", "理解", "沟通"], "通识拓展315·存量卡补题"),
    ("QB-1186", "感觉冷了身体会有什么反应？该怎么照顾自己？", "生活咨询", "情感陪伴",
     ["冷", "穿", "暖和", "感冒"], "通识拓展315·存量卡补题"),
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
    bank["version"] = "v5.85"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
