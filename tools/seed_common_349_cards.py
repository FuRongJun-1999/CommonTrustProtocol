# -*- coding: utf-8 -*-
"""seed_common_349_cards.py · 通识拓展批次349·存量卡补题·清单中部（幂等）

349：4 张卡补 4 题（QB-1285~1288）——圆的性质/紧张情绪/独立性检验/
     折线统计图
     清单索引2441-2482段。预检已过（QB-1285~1288 可用）。
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
    ("QB-1285", "圆有什么基本性质？同圆中直径和弦是什么关系？", "数学", "学科直答",
     ["圆", "圆心", "半径", "直径"], "通识拓展349·存量卡补题"),
    ("QB-1286", "紧张是正常的吗？怎么缓解紧张情绪？", "生活咨询", "情感陪伴",
     ["紧张", "正常", "在乎", "深呼吸"], "通识拓展349·存量卡补题"),
    ("QB-1287", "独立性检验是什么？卡方检验怎么判断变量是否相关？", "数学", "学科直答",
     ["独立性", "卡方", "分类变量", "统计"], "通识拓展349·存量卡补题"),
    ("QB-1288", "折线统计图适合表现什么数据？它有什么优势？", "数学", "学科直答",
     ["折线", "变化", "趋势", "上升下降"], "通识拓展349·存量卡补题"),
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
    bank["version"] = "v6.15"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
