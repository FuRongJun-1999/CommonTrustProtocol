# -*- coding: utf-8 -*-
"""seed_common_247_cards.py · 通识拓展批次247·存量卡补题（幂等）

247：4 张通识卡补 4 题（QB-931~934）——装修甲醛/晨练晚练/梦游/久坐危害
     卡已在库（触发词完整），零新卡。预检已过（QB-931~934 可用）。
     注：潮汐卡与 QB-669 重叠跳过；泡茶水温留下一批。
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
    ("QB-931", "装修甲醛怎么除？新房通风多久能入住？", "生活常识", "技术直答",
     ["通风", "缓释", "3-15", "入住"], "通识拓展247·存量卡补题"),
    ("QB-932", "早上锻炼好还是晚上锻炼好？晨练要注意什么？", "生活常识", "技术直答",
     ["晨峰", "血液黏稠", "日出", "傍晚"], "通识拓展247·存量卡补题"),
    ("QB-933", "梦游是怎么回事？梦游的人知道自己在做什么吗？能叫醒吗？",
     "生活常识", "技术直答",
     ["深睡眠", "不知道", "叫醒", "安全"], "通识拓展247·存量卡补题"),
    ("QB-934", "久坐有什么危害？坐多久该起来活动一次？", "生活常识", "技术直答",
     ["血栓", "腰颈椎", "45", "胰岛素"], "通识拓展247·存量卡补题"),
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
    bank["version"] = "v5.18"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
