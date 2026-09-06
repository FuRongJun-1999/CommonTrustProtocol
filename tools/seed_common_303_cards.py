# -*- coding: utf-8 -*-
"""seed_common_303_cards.py · 通识拓展批次303·存量卡补题·清单中部（幂等）

303：4 张卡补 4 题（QB-1139~1142）——角/动态类型/党的领导/气固分离
     清单索引2000起。预检已过（QB-1139~1142 可用）。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("QB-1139", "角是怎么组成的？角的大小与边的长短有关吗？", "数学", "学科直答",
     ["顶点", "两条边", "张开程度", "射线"], "通识拓展303·存量卡补题"),
    ("QB-1140", "动态类型语言是什么？什么是鸭子类型？", "编程", "学科直答",
     ["动态类型", "运行时", "鸭子类型", "原型"], "通识拓展303·存量卡补题"),
    ("QB-1141", "中国特色社会主义最本质的特征是什么？党的宗旨是什么？", "政治", "学科直答",
     ["党的领导", "本质特征", "为人民服务", "宗旨"], "通识拓展303·存量卡补题"),
    ("QB-1142", "气固分离有哪些常见设备？它们分别靠什么原理工作？", "化学", "学科直答",
     ["旋风分离", "袋式除尘", "静电除尘", "离心"], "通识拓展303·存量卡补题"),
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
    bank["version"] = "v5.73"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
