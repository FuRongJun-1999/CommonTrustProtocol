# -*- coding: utf-8 -*-
"""seed_common_263_cards.py · 通识拓展批次263·存量卡补题（幂等）

263：4 张卡补 4 题（QB-979~982）——牙膏色条谣言/晒被子/保鲜膜微波/疣瘊子
     卡已在库（触发词完整），零新卡。预检已过（QB-979~982 可用）。
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
    ("QB-979", "牙膏尾部的色条是什么？绿色代表纯天然吗？", "生活常识", "技术直答",
     ["色条", "谣言", "定位", "印刷"], "通识拓展263·存量卡补题"),
    ("QB-980", "被子怎么晒才对？晒多久？蚕丝被能晒吗？", "生活常识", "技术直答",
     ["紫外线", "除螨", "2-3", "蚕丝"], "通识拓展263·存量卡补题"),
    ("QB-981", "保鲜膜可以进微波炉加热吗？PVC保鲜膜有什么危害？", "生活常识", "技术直答",
     ["材质", "PE", "PVC", "耐温"], "通识拓展263·存量卡补题"),
    ("QB-982", "瘊子是什么？跖疣和鸡眼怎么区分？", "生活常识", "技术直答",
     ["HPV", "病毒", "跖疣", "鸡眼"], "通识拓展263·存量卡补题"),
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
    bank["version"] = "v5.34"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
