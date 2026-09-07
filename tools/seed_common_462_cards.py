# -*- coding: utf-8 -*-
"""seed_common_462_cards.py · 通识拓展批次462·存量卡补题（幂等）

462：3 张卡补 3 题（QB-1621~1623）——光学与生物智慧三连：
    凸透镜与凹透镜 kp_card_lens / 候鸟迁徙 kp_card_migration /
    保护色与拟态 kp_card_camouflage。均已在库，无对应题
    （凸透镜与 QB-1457 眼近视矫正题区分：本题聚焦透镜成像原理）。
预检已过（QB-1621~1623 可用，三主题精确关键词 0 覆盖）。
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
    ("QB-1621", "凸透镜和凹透镜有什么区别？放大镜用的是哪种透镜？",
     "物理基础", "技术直答",
     ["凸透镜", "凹透镜", "会聚", "发散"], "通识拓展462·存量卡补题"),
    ("QB-1622", "候鸟迁徙靠什么认路？迁徙最远的鸟是哪种？",
     "自然与生物", "技术直答",
     ["候鸟", "迁徙", "导航", "北极燕鸥"], "通识拓展462·存量卡补题"),
    ("QB-1623", "什么是保护色和拟态？变色龙为什么变色？",
     "自然与生物", "技术直答",
     ["保护色", "拟态", "变色龙", "枯叶蝶"], "通识拓展462·存量卡补题"),
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
    bank["version"] = "v7.32"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
