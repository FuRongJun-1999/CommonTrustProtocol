# -*- coding: utf-8 -*-
"""seed_common_353_cards.py · 通识拓展批次353·存量卡补题·清单中部（幂等）

353：4 张卡补 4 题（QB-1295~1298）——指针与引用/条形统计图/收集与整理/
     生气情绪
     清单索引2484-2496段。预检已过（QB-1295~1298 可用）。
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
    ("QB-1295", "指针和引用有什么区别？为什么说内存安全很关键？", "编程", "学科直答",
     ["指针", "引用", "别名", "生命周期"], "通识拓展353·存量卡补题"),
    ("QB-1296", "条形统计图适合表现什么数据？有什么优势？", "数学", "学科直答",
     ["条形", "直条", "数量", "一眼"], "通识拓展353·存量卡补题"),
    ("QB-1297", "数据收集有什么方法？怎么整理数据看得更清楚？", "数学", "学科直答",
     ["正字", "表格", "收集", "整理"], "通识拓展353·存量卡补题"),
    ("QB-1298", "生气的时候怎么控制情绪？", "生活咨询", "情感陪伴",
     ["生气", "深呼吸", "冷静", "再说"], "通识拓展353·存量卡补题"),
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
    bank["version"] = "v6.19"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
