# -*- coding: utf-8 -*-
"""seed_common_299_cards.py · 通识拓展批次299·存量卡补题·清单中部（幂等）

299：5 张卡补 5 题（QB-1127~1131）——内能/硼族元素/陆地和海洋/表观遗传学/
     简便运算
     清单索引1800起（人工避开已有题的容积卡）。预检已过（QB-1127~1131 可用）。
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
             "BCS", "B2H6"}


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
    ("QB-1127", "什么是内能？改变内能有哪两种方式？", "物理", "学科直答",
     ["内能", "做功", "热传递", "温度"], "通识拓展299·存量卡补题"),
    ("QB-1128", "硼族元素有什么特点？铝为什么是两性金属？", "化学", "学科直答",
     ["硼族", "缺电子", "铝", "两性"], "通识拓展299·存量卡补题"),
    ("QB-1129", "地球上海洋和陆地各占多少比例？七大洲中哪个最大？", "地理学", "学科直答",
     ["71%", "29%", "七大洲", "太平洋"], "通识拓展299·存量卡补题"),
    ("QB-1130", "什么是表观遗传？它和基因突变有什么区别？", "生物", "学科直答",
     ["表观遗传", "甲基化", "可遗传", "序列"], "通识拓展299·存量卡补题"),
    ("QB-1131", "简便运算中 25×4 和 125×8 的作用是什么？", "数学", "学科直答",
     ["25", "125", "凑整", "简便"], "通识拓展299·存量卡补题"),
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
    bank["version"] = "v5.70"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
