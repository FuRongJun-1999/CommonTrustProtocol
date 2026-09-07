# -*- coding: utf-8 -*-
"""seed_common_483_cards.py · 通识拓展批次483·存量卡补题（幂等）

483：3 张卡补 3 题（QB-1639~1641已用，本批QB-1684~1686）——
    历史事件与人物三连：靖康之变 kp_card_jingkang /
    中国古代四大发明（四大发明历史影响角度，QB-1559 已出
    「是什么与发明人」，本题出「历史影响」角度——若内容重叠
    则以丝绸之路取代）：丝绸之路 kp_card_silkroad。
预检已过（QB-1684~1686 可用，三主题精确关键词 0 覆盖）。
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
    ("QB-1684", "靖康之变发生在哪一年？它对北宋有什么影响？",
     "历史常识", "技术直答",
     ["靖康之变", "北宋", "金", "灭亡"], "通识拓展483·存量卡补题"),
    ("QB-1685", "丝绸之路是谁开通的？它连接了哪些文明？",
     "历史常识", "技术直答",
     ["丝绸之路", "张骞", "西域", "贸易"], "通识拓展483·存量卡补题"),
    ("QB-1686", "四大发明对世界文明进程有什么影响？",
     "历史常识", "技术直答",
     ["四大发明", "世界文明", "传播", "影响"], "通识拓展483·存量卡补题"),
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
    bank["version"] = "v7.50"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
