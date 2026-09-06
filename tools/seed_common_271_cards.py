# -*- coding: utf-8 -*-
"""seed_common_271_cards.py · 通识拓展批次271·存量卡补题·清单中部（幂等）

271：6 张学术卡补 6 题（QB-1028~1033）——椭圆/隐函数定理/三羧酸循环/
     波的干涉衍射/质点运动学/实数完备性
     清单头部耗尽，转中部抽样（索引300起）。预检已过（QB-1028~1033 可用）。
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
             "FADH2"}


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
    ("QB-1028", "椭圆的标准方程是什么？什么是椭圆的焦点？", "数学", "学科直答",
     ["椭圆", "焦点", "标准方程", "轨迹"], "通识拓展271·存量卡补题"),
    ("QB-1029", "隐函数定理的条件和结论是什么？", "数学", "学科直答",
     ["隐函数", "偏导", "连续", "唯一"], "通识拓展271·存量卡补题"),
    ("QB-1030", "三羧酸循环发生在细胞的哪个部位？有什么意义？", "生物", "学科直答",
     ["线粒体", "乙酰", "氧化", "能量"], "通识拓展271·存量卡补题"),
    ("QB-1031", "波的干涉和衍射分别是什么？发生干涉的条件是什么？", "物理", "学科直答",
     ["干涉", "衍射", "频率相同", "叠加"], "通识拓展271·存量卡补题"),
    ("QB-1032", "质点运动学中位置、速度、加速度之间是什么关系？", "物理", "学科直答",
     ["位置矢量", "速度", "加速度", "导数"], "通识拓展271·存量卡补题"),
    ("QB-1033", "实数完备性是什么？六大等价定理包括哪些？", "数学", "学科直答",
     ["完备", "确界", "单调有界", "闭区间套"], "通识拓展271·存量卡补题"),
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
    bank["version"] = "v5.42"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
