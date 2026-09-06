# -*- coding: utf-8 -*-
"""seed_common_265_cards.py · 通识拓展批次265·1000题冲刺前哨（纯存量卡补题·幂等）

265：8 张卡补 8 题（QB-985~992），题库 968→976：
     方差/协方差相关系数/基因工程/种子传播/潜艇浮沉/喝酒脸红/耳机线打结/KKT条件
     卡已在库（触发词完整），零新卡。预检已过（QB-985~992 可用）。
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
    ("QB-985", "方差是什么？它反映数据的什么特征？怎么计算？", "数学", "学科直答",
     ["方差", "分散", "期望", "平方"], "通识拓展265·存量卡补题"),
    ("QB-986", "协方差和相关系数有什么关系？相关系数的范围是多少？", "数学", "学科直答",
     ["协方差", "相关系数", "标准化", "-1"], "通识拓展265·存量卡补题"),
    ("QB-987", "基因工程的基本操作步骤是什么？有什么应用？", "生物", "学科直答",
     ["目的基因", "载体", "限制酶", "重组"], "通识拓展265·存量卡补题"),
    ("QB-988", "种子靠什么传播？蒲公英和苍耳分别用什么方式？", "生物", "学科直答",
     ["风力", "动物", "水", "弹射"], "通识拓展265·存量卡补题"),
    ("QB-989", "潜艇为什么能上浮下潜？它和鱼类的原理有什么区别？", "基础科学", "技术直答",
     ["水舱", "注水", "排水", "鱼鳔"], "通识拓展265·存量卡补题"),
    ("QB-990", "喝酒为什么会脸红？喝酒脸红的人是不是酒量好？", "生活常识", "技术直答",
     ["乙醛", "脱氢酶", "基因", "有害"], "通识拓展265·存量卡补题"),
    ("QB-991", "耳机线为什么放包里总会打结？怎么收纳不打结？", "生活常识", "技术直答",
     ["打结", "随机", "组合", "收纳"], "通识拓展265·存量卡补题"),
    ("QB-992", "KKT条件是什么？什么优化问题需要用到它？", "数学", "学科直答",
     ["不等式约束", "必要条件", "对偶", "最优"], "通识拓展265·存量卡补题"),
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
    bank["version"] = "v5.36"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
