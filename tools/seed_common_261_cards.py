# -*- coding: utf-8 -*-
"""seed_common_261_cards.py · 通识拓展批次261·存量卡补题（幂等）

261：4 张卡补 4 题（QB-973~976）——质数/口臭来源/回南天/中国土地资源
     卡已在库（触发词完整），零新卡。预检已过（QB-973~976 可用）。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP"}


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
    ("QB-973", "质数是什么？最小的质数是几？质数有多少个？", "数学", "学科直答",
     ["质数", "整除", "2", "无穷"], "通识拓展261·存量卡补题"),
    ("QB-974", "口臭是什么原因引起的？怎么根治？", "生活常识", "技术直答",
     ["舌苔", "厌氧菌", "硫化物", "牙周"], "通识拓展261·存量卡补题"),
    ("QB-975", "回南天是什么？为什么开窗反而更潮？怎么防潮？", "生活常识", "技术直答",
     ["回南天", "凝结", "开窗", "防潮"], "通识拓展261·存量卡补题"),
    ("QB-976", "中国土地资源有什么特点？为什么要守住18亿亩耕地红线？",
     "地理学", "学科直答",
     ["人均", "耕地", "红线", "国策"], "通识拓展261·存量卡补题"),
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
    bank["version"] = "v5.32"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
