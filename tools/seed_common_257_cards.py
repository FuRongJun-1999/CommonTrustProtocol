# -*- coding: utf-8 -*-
"""seed_common_257_cards.py · 通识拓展批次257·存量卡补题（幂等）

257：4 张卡补 4 题（QB-961~964）——酒店入住/木耳米酵菌酸/体位性低血压/贝叶斯公式
     卡已在库（触发词完整），零新卡。预检已过（QB-961~964 可用）。
     注：流鼻血卡系清单误报（已有 QB-723），跳过。
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
    ("QB-961", "酒店退房时间是几点？入住登记和押金有什么规矩？", "生活常识", "技术直答",
     ["实名", "登记", "押金", "12"], "通识拓展257·存量卡补题"),
    ("QB-962", "木耳泡多久会中毒？米酵菌酸是什么？", "生活常识", "技术直答",
     ["久泡", "米酵菌酸", "耐热", "中毒"], "通识拓展257·存量卡补题"),
    ("QB-963", "蹲久了站起来为什么会眼前发黑？要紧吗？", "生活常识", "技术直答",
     ["体位性", "低血压", "回心血量", "供血"], "通识拓展257·存量卡补题"),
    ("QB-964", "全概率公式和贝叶斯公式分别是什么？怎么用？", "数学", "学科直答",
     ["全概率", "分解", "贝叶斯", "后验"], "通识拓展257·存量卡补题"),
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
    bank["version"] = "v5.28"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
