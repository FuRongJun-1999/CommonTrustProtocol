# -*- coding: utf-8 -*-
"""seed_common_243_cards.py · 通识拓展批次243·存量卡补题（幂等）

243：4 张通识卡补 4 题（QB-919~922）——新航路开辟/驾驶证记分/户口居住证/荨麻疹
     卡已在库（触发词完整），零新卡。预检已过（QB-919~922 可用）。
     清单升级：cardless_ready_20260906.json（2531张有内容，滤除401空壳）。
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
    ("QB-919", "新航路开辟的原因是什么？哥伦布和麦哲伦分别完成了什么？", "历史", "技术直答",
     ["香料", "哥伦布", "美洲", "麦哲伦", "环球"], "通识拓展243·存量卡补题"),
    ("QB-920", "驾驶证记分周期是多久？记满12分怎么办？酒驾怎么处罚？", "生活常识", "技术直答",
     ["12", "记分", "酒驾", "醉驾"], "通识拓展243·存量卡补题"),
    ("QB-921", "户口和居住证有什么区别？居住证怎么办理？", "生活常识", "技术直答",
     ["户籍", "居住证", "常住", "办理"], "通识拓展243·存量卡补题"),
    ("QB-922", "荨麻疹是什么？怎么引起的？如何治疗？", "生活常识", "技术直答",
     ["风团", "组胺", "过敏", "抗组胺"], "通识拓展243·存量卡补题"),
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
    bank["version"] = "v5.14"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
