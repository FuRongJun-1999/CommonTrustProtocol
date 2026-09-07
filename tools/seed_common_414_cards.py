# -*- coding: utf-8 -*-
"""seed_common_414_cards.py · 通识拓展批次414·存量卡补题（幂等）

414：3 张卡补 3 题（QB-1480~1482）——认识国家/敏捷开发/光的干涉
     清单索引360与450段取卡（换元积分/镧系候选查重已有题被排除；
     光的干涉与 QB-1031 机械波干涉区分：本题为光波杨氏双缝角度）。
预检已过（QB-1480~1482 可用）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("QB-1480", "日本、印度、俄罗斯三国的经济地理各有什么特点？",
     "地理常识", "技术直答",
     ["日本", "印度", "俄罗斯", "经济"], "通识拓展414·存量卡补题"),
    ("QB-1481", "什么是敏捷开发？它和瀑布式开发有什么区别？",
     "软件工程", "技术直答",
     ["敏捷开发", "迭代", "瀑布", "需求"], "通识拓展414·存量卡补题"),
    ("QB-1482", "什么是杨氏双缝干涉？这个实验证明了什么？",
     "物理基础", "技术直答",
     ["光的干涉", "双缝", "条纹", "波动"], "通识拓展414·存量卡补题"),
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
    bank["version"] = "v6.85"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
