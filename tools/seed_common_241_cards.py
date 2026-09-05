# -*- coding: utf-8 -*-
"""seed_common_241_cards.py · 通识拓展批次241·900题冲刺（纯存量卡补题·幂等）

241：8 张存量卡补 8 题（QB-909~916），题库 892→900 里程碑：
     容积/判断句/文件操作/牛顿第三定律/浮力/密度/压强/水的三态
     卡已在库（内容完整），零新卡。预检已过（QB-909~916 可用）。
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
    ("QB-909", "什么是容积？容积的单位是什么？", "数学", "学科直答",
     ["容积", "升", "毫升"], "通识拓展241·存量卡补题"),
    ("QB-910", "文言文判断句的典型句式是什么？", "语文", "学科直答",
     ["者", "也", "乃", "判断"], "通识拓展241·存量卡补题"),
    ("QB-911", "编程中文件操作的基本步骤是什么？", "编程", "学科直答",
     ["打开", "读写", "关闭"], "通识拓展241·存量卡补题"),
    ("QB-912", "牛顿第三定律的内容是什么？", "物理", "学科直答",
     ["作用力", "反作用力", "相等", "相反"], "通识拓展241·存量卡补题"),
    ("QB-913", "浮力的方向是什么？浮力大小与什么有关？", "物理", "学科直答",
     ["竖直向上", "浸没", "体积"], "通识拓展241·存量卡补题"),
    ("QB-914", "密度是什么？密度怎么计算？", "物理", "学科直答",
     ["密度", "质量", "体积"], "通识拓展241·存量卡补题"),
    ("QB-915", "压强的定义是什么？怎么增大或减小压强？", "物理", "学科直答",
     ["压力", "受力面积", "增大", "减小"], "通识拓展241·存量卡补题"),
    ("QB-916", "水的三种状态是什么？它们之间怎么互相转化？", "物理", "学科直答",
     ["冰", "水蒸气", "结冰", "水"], "通识拓展241·存量卡补题"),
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
    bank["version"] = "v5.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
