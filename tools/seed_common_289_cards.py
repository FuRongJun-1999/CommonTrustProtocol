# -*- coding: utf-8 -*-
"""seed_common_289_cards.py · 通识拓展批次289·存量卡补题·清单中部（幂等）

289：5 张卡补 5 题（QB-1092~1096）——羧酸酯/染色体变异/笔画笔顺/高尔基体/
     价格策略
     清单索引1300起。预检已过（QB-1092~1096 可用）。
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
             "BCS"}


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
    ("QB-1092", "酯化反应的规律是什么？「酸脱羟基醇脱氢」怎么理解？", "化学", "学科直答",
     ["酯化", "羧酸", "醇", "皂化"], "通识拓展289·存量卡补题"),
    ("QB-1093", "染色体结构变异有哪几种类型？唐氏综合征是怎么回事？", "生物", "学科直答",
     ["缺失", "易位", "21三体", "唐氏"], "通识拓展289·存量卡补题"),
    ("QB-1094", "汉字的基本笔画有哪些？笔顺有什么规则？", "语文", "学科直答",
     ["横竖撇点折", "笔顺", "先横后竖", "从上到下"], "通识拓展289·存量卡补题"),
    ("QB-1095", "高尔基体有什么功能？它在蛋白质运输中起什么作用？", "生物", "学科直答",
     ["加工", "分选", "包装", "糖基化"], "通识拓展289·存量卡补题"),
    ("QB-1096", "常见的定价策略有哪些？撇脂定价和渗透定价有什么区别？",
     "职场", "学科直答",
     ["撇脂", "渗透", "心理定价", "成本"], "通识拓展289·存量卡补题"),
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
    bank["version"] = "v5.60"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
