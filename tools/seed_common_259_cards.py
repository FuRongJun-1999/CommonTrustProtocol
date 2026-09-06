# -*- coding: utf-8 -*-
"""seed_common_259_cards.py · 通识拓展批次259·存量卡补题（幂等）

259：4 张卡补 4 题（QB-967~970）——切洋葱流泪/腹泻补液/筷子文化禁忌/雨天水滑
     卡已在库（触发词完整），零新卡。预检已过（QB-967~970 可用）。
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
    ("QB-967", "切洋葱为什么会流泪？怎么切洋葱不辣眼睛？", "生活常识", "技术直答",
     ["催泪因子", "挥发", "冷藏", "刺激"], "通识拓展259·存量卡补题"),
    ("QB-968", "拉肚子最要紧的是什么？腹泻能不能马上吃止泻药？", "生活常识", "技术直答",
     ["脱水", "补液盐", "电解质", "止泻药"], "通识拓展259·存量卡补题"),
    ("QB-969", "筷子为什么不能插在饭上？筷子有哪些使用禁忌？", "文化", "技术直答",
     ["香", "禁忌", "筷子", "礼仪"], "通识拓展259·存量卡补题"),
    ("QB-970", "雨天开车水滑效应是怎么回事？发生了怎么办？", "生活常识", "技术直答",
     ["水滑", "积水", "松油门", "急刹"], "通识拓展259·存量卡补题"),
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
    bank["version"] = "v5.30"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
