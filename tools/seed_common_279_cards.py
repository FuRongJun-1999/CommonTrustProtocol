# -*- coding: utf-8 -*-
"""seed_common_279_cards.py · 通识拓展批次279·存量卡补题·清单中部（幂等）

279：5 张卡补 5 题（QB-1056~1060）——死锁/设计模式/B树B+树/回归分析/细胞膜结构
     清单索引700起。预检已过（QB-1056~1060 可用）。
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
             "FADH2", "Vmax", "Km"}


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
    ("QB-1056", "什么是死锁？死锁发生的四个必要条件是什么？", "编程", "学科直答",
     ["死锁", "互斥", "持有等待", "循环等待"], "通识拓展279·存量卡补题"),
    ("QB-1057", "设计模式分哪几大类？单例模式和工厂模式是什么？", "编程", "学科直答",
     ["创建型", "结构型", "行为型", "单例"], "通识拓展279·存量卡补题"),
    ("QB-1058", "B树和B+树有什么区别？数据库索引用哪个？", "编程", "学科直答",
     ["B树", "B+树", "叶子", "索引"], "通识拓展279·存量卡补题"),
    ("QB-1059", "回归分析是什么？最小二乘法怎么理解？", "数学", "学科直答",
     ["回归", "线性", "最小二乘", "拟合"], "通识拓展279·存量卡补题"),
    ("QB-1060", "细胞膜的流动镶嵌模型是什么结构？为什么说膜是流动的？", "生物", "学科直答",
     ["磷脂双分子层", "镶嵌", "蛋白质", "流动性"], "通识拓展279·存量卡补题"),
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
    bank["version"] = "v5.50"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
