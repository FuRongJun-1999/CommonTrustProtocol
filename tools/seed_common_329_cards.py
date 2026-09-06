# -*- coding: utf-8 -*-
"""seed_common_329_cards.py · 通识拓展批次329·存量卡补题·清单中部（幂等）

329：4 张卡补 4 题（QB-1225~1228）——抽样调查/数对/焦虑陪伴/孝亲敬长
     清单索引2255-2277段。预检已过（QB-1225~1228 可用）。
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
    ("QB-1225", "什么是抽样调查？样本为什么要具有代表性？", "数学", "学科直答",
     ["抽样", "样本", "代表性", "随机"], "通识拓展329·存量卡补题"),
    ("QB-1226", "什么是数对？数对怎么确定位置？", "数学", "学科直答",
     ["数对", "列", "行", "位置"], "通识拓展329·存量卡补题"),
    ("QB-1227", "感到焦虑怎么办？怎么缓解焦虑情绪？", "生活咨询", "情感陪伴",
     ["焦虑", "能做的", "时间", "倾诉"], "通识拓展329·存量卡补题"),
    ("QB-1228", "为什么要孝亲敬长？怎么做才是孝敬父母？", "政治", "学科直答",
     ["孝敬", "传统美德", "尊敬", "分担"], "通识拓展329·存量卡补题"),
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
    bank["version"] = "v5.99"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
