# -*- coding: utf-8 -*-
"""seed_common_309_cards.py · 通识拓展批次309·存量卡补题·清单中部（幂等）

309：4 张卡补 4 题（QB-1159~1162）——因式分解/专注方法/婚姻家庭/情绪陪伴
     清单索引2400起。预检已过（QB-1159~1162 可用）。
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
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("QB-1159", "什么是因式分解？提公因式法和公式法分别怎么用？", "数学", "学科直答",
     ["因式分解", "提公因式", "公式法", "整式"], "通识拓展309·存量卡补题"),
    ("QB-1160", "怎么保持专注？番茄钟怎么用？", "职场", "技术直答",
     ["番茄钟", "25", "手机隔离", "单任务"], "通识拓展309·存量卡补题"),
    ("QB-1161", "结婚需要什么条件？夫妻财产怎么界定？", "生活常识", "技术直答",
     ["结婚条件", "程序", "夫妻财产", "继承"], "通识拓展309·存量卡补题"),
    ("QB-1162", "离家久了想家怎么办？这种情绪正常吗？", "生活咨询", "情感陪伴",
     ["想家", "正常", "打电话", "联系"], "通识拓展309·存量卡补题"),
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
    bank["version"] = "v5.79"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
