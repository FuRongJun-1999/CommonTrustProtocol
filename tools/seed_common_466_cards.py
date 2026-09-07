# -*- coding: utf-8 -*-
"""seed_common_466_cards.py · 通识拓展批次466·存量卡补题（幂等）

466：3 张卡补 3 题（QB-1633~1635）——成长生活三连：化合反应
    kp_735239737 / 友谊 kp_738979074 / 网络生活 kp_7608717010。
均已在库，无对应题（网络生活与 QB-1477 信息茧房、QB-1619
密码安全题区分角度：本题为健康上网与文明用网）。
预检已过（QB-1633~1635 可用，三主题精确关键词 0 覆盖）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("QB-1633", "什么是化合反应？它和氧化反应有什么关系？",
     "化学基础", "技术直答",
     ["化合反应", "多变一", "氧化反应", "化学"], "通识拓展466·存量卡补题"),
    ("QB-1634", "怎么建立和维护真正的友谊？择友要注意什么？",
     "生活常识", "技术直答",
     ["友谊", "真诚", "信任", "择友"], "通识拓展466·存量卡补题"),
    ("QB-1635", "网络生活有哪些利与弊？怎么做到文明上网？",
     "生活常识", "技术直答",
     ["网络生活", "文明上网", "隐私", "沉迷"], "通识拓展466·存量卡补题"),
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
    bank["version"] = "v7.36"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
