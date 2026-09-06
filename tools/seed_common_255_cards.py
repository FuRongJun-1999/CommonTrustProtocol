# -*- coding: utf-8 -*-
"""seed_common_255_cards.py · 通识拓展批次255·存量卡补题（幂等）

255：4 张卡补 4 题（QB-955~958）——乙烯催熟/挑螃蟹死蟹/能量流动/生态位
     卡已在库（触发词完整），零新卡。预检已过（QB-955~958 可用）。
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
    ("QB-955", "苹果和香蕉放一起为什么会加速成熟？乙烯催熟的原理是什么？",
     "生活常识", "技术直答",
     ["乙烯", "催熟", "激素", "正反馈"], "通识拓展255·存量卡补题"),
    ("QB-956", "怎么挑螃蟹？死螃蟹为什么不能吃？", "生活常识", "技术直答",
     ["活蟹", "组胺", "活煮", "中毒"], "通识拓展255·存量卡补题"),
    ("QB-957", "生态系统中能量流动有什么特点？为什么食物链不能太长？",
     "生物", "学科直答",
     ["单向", "递减", "十分之一", "营养级"], "通识拓展255·存量卡补题"),
    ("QB-958", "什么是生态位？为什么同一区域两种生物不能长期占据同一生态位？",
     "生物", "学科直答",
     ["生态位", "竞争排斥", "资源", "分化"], "通识拓展255·存量卡补题"),
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
    bank["version"] = "v5.26"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
