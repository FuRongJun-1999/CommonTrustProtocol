# -*- coding: utf-8 -*-
"""seed_common_388_cards.py · 通识拓展批次388·存量卡补题（幂等）

388：3 张卡补 3 题（QB-1402~1404）——常见的碱/陆地和海洋/四个自信
     清单索引1800与2200段取卡（大爆炸/恒星/食品保存候选经程序化
     查重已有题被排除）。预检已过（QB-1402~1404 可用，三主题
     精确关键词 0 覆盖）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("QB-1402", "烧碱和熟石灰分别是什么？使用时要注意什么？",
     "化学基础", "技术直答",
     ["烧碱", "熟石灰", "碱", "腐蚀"], "通识拓展388·存量卡补题"),
    ("QB-1403", "地球上海洋和陆地的面积比例是多少？分布有什么特点？",
     "地理常识", "技术直答",
     ["海洋", "陆地", "比例", "分布"], "通识拓展388·存量卡补题"),
    ("QB-1404", "「四个自信」分别指什么？",
     "政治常识", "技术直答",
     ["四个自信", "道路", "制度", "文化"], "通识拓展388·存量卡补题"),
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
    bank["version"] = "v6.58"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
