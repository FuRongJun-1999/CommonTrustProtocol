# -*- coding: utf-8 -*-
"""seed_common_321_cards.py · 通识拓展批次321·存量卡补题（幂等）

321：4 张学术卡补 4 题（QB-1201~1204）——极限运算法则/最短路径算法/
     泰勒公式/带电粒子在磁场中运动
     预检已过（QB-1201~1204 可用）。
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
             "BCS", "B2H6", "borrow", "Rust", "Dijkstra", "Bellman",
             "Floyd", "logV"}


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
    ("QB-1201", "极限的四则运算法则是什么？使用时要注意什么？", "数学", "学科直答",
     ["极限", "四则", "存在", "分别"], "通识拓展321·存量卡补题"),
    ("QB-1202", "最短路径问题有哪些经典算法？各适用于什么场景？", "编程", "学科直答",
     ["Dijkstra", "非负权", "Bellman", " Floyd"], "通识拓展321·存量卡补题"),
    ("QB-1203", "泰勒公式是什么？它为什么能用多项式逼近函数？", "数学", "学科直答",
     ["泰勒", "多项式", "逼近", "展开"], "通识拓展321·存量卡补题"),
    ("QB-1204", "带电粒子垂直进入匀强磁场会做什么运动？轨道半径由什么决定？",
     "物理", "学科直答",
     ["洛伦兹力", "圆周", "半径", "匀速"], "通识拓展321·存量卡补题"),
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
    bank["version"] = "v5.91"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
