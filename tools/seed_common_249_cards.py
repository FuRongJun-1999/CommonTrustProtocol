# -*- coding: utf-8 -*-
"""seed_common_249_cards.py · 通识拓展批次249·存量卡补题+复测锚定（幂等）

249：4 张通识卡补 4 题（QB-937~940）——泡茶水温/地铁乘车/冰川/蚊子包止痒
     另：第5次随机复测锚定（seed=20260906 抽16题，全量920/920内含通过）。
     预检已过（QB-937~940 可用）。
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
    ("QB-937", "泡绿茶用多少度的水？不同茶叶的水温有什么讲究？", "生活常识", "技术直答",
     ["绿茶", "75", "红茶", "洗茶"], "通识拓展249·存量卡补题"),
    ("QB-938", "地铁安检什么不能带？怎么坐地铁？", "生活常识", "技术直答",
     ["安检", "管制刀", "易燃", "过闸"], "通识拓展249·存量卡补题"),
    ("QB-939", "冰川是什么？地球多少淡水储存在冰川里？冰川会移动吗？",
     "地理学", "学科直答",
     ["冰川", "70%", "淡水", "移动"], "通识拓展249·存量卡补题"),
    ("QB-940", "被蚊子咬了为什么会痒？怎么止痒？", "生活常识", "技术直答",
     ["蚊子", "唾液", "组胺", "止痒"], "通识拓展249·存量卡补题"),
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
    bank["version"] = "v5.20"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
