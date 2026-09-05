# -*- coding: utf-8 -*-
"""seed_common_245_cards.py · 通识拓展批次245·存量卡补题（幂等）

245：4 张通识卡补 4 题（QB-925~928）——科学减重/折扣满减/低头族颈椎/鬼压床
     卡已在库（触发词完整），零新卡。预检已过（QB-925~928 可用）。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("QB-925", "怎么减肥才科学？减重每周多少合适？为什么节食容易反弹？",
     "生活常识", "技术直答",
     ["热量缺口", "7700", "反弹", "肌肉"], "通识拓展245·存量卡补题"),
    ("QB-926", "打八折怎么计算？满300减100和7折哪个划算？", "生活常识", "技术直答",
     ["八折", "0.8", "满减", "折合"], "通识拓展245·存量卡补题"),
    ("QB-927", "低头玩手机颈椎承受多大压力？颈椎病怎么预防？", "生活常识", "技术直答",
     ["低头", "颈椎", "27", "60"], "通识拓展245·存量卡补题"),
    ("QB-928", "鬼压床是什么？睡眠瘫痪怎么解除？有危险吗？", "生活常识", "技术直答",
     ["睡眠瘫痪", "REM", "动不了", "危险"], "通识拓展245·存量卡补题"),
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
    bank["version"] = "v5.16"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
