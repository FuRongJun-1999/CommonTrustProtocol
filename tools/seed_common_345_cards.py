# -*- coding: utf-8 -*-
"""seed_common_345_cards.py · 通识拓展批次345·存量卡补题·清单中部（幂等）

345：4 张卡补 4 题（QB-1273~1276）——羡慕/整数/向上沟通/头晕
     清单索引2442-2465段。预检已过（QB-1273~1276 可用）。
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
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("QB-1273", "羡慕别人怎么办？怎么调整这种心态？", "生活咨询", "情感陪伴",
     ["羡慕", "自己的路", "过好", "心态"], "通识拓展345·存量卡补题"),
    ("QB-1274", "整数包括哪些数？数数时怎么理解整数？", "数学", "学科直答",
     ["整数", "数数", "表示", "多少"], "通识拓展345·存量卡补题"),
    ("QB-1275", "怎么向上沟通？向领导汇报有什么技巧？", "职场", "技术直答",
     ["同步", "风险", "选择题", "结论先行"], "通识拓展345·存量卡补题"),
    ("QB-1276", "头晕是怎么回事？什么时候需要看医生？", "生活常识", "技术直答",
     ["头晕", "休息", "进食", "就医"], "通识拓展345·存量卡补题"),
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
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.14"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
