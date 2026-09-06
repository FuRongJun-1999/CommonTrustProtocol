# -*- coding: utf-8 -*-
"""seed_common_253_cards.py · 通识拓展批次253·存量卡补题（幂等）

253：4 张卡补 4 题（QB-949~952）——烫发染发化学/手机进水/跑步岔气/蛋白质
     卡已在库（触发词完整），零新卡。预检已过（QB-949~952 可用）。
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
    ("QB-949", "烫发的化学原理是什么？二硫键和头发卷曲有什么关系？", "生活常识", "技术直答",
     ["二硫键", "还原剂", "氧化剂", "定型"], "通识拓展253·存量卡补题"),
    ("QB-950", "手机进水了怎么办？放米缸有用吗？能马上充电吗？", "生活常识", "技术直答",
     ["关机", "干燥剂", "充电", "送修"], "通识拓展253·存量卡补题"),
    ("QB-951", "跑步为什么会岔气？岔气了怎么处理？", "生活常识", "技术直答",
     ["膈肌", "痉挛", "呼吸", "减速"], "通识拓展253·存量卡补题"),
    ("QB-952", "蛋白质的基本单位是什么？它为什么是生命活动的主要承担者？",
     "生物", "学科直答",
     ["氨基酸", "肽链", "脱水缩合", "承担者"], "通识拓展253·存量卡补题"),
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
    bank["version"] = "v5.24"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
