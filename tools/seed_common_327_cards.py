# -*- coding: utf-8 -*-
"""seed_common_327_cards.py · 通识拓展批次327·存量卡补题·清单中部（幂等）

327：4 张卡补 4 题（QB-1219~1222）——集合运算/概要写作/反比例/用药安全
     清单索引2230-2254段。预检已过（QB-1219~1222 可用）。
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
    ("QB-1219", "交集、并集、补集分别是什么意思？", "数学", "学科直答",
     ["交集", "并集", "补集", "公共元素"], "通识拓展327·存量卡补题"),
    ("QB-1220", "概要写作有什么要求？怎么写好概要？", "语文", "学科直答",
     ["概括", "要点", "简洁", "连贯"], "通识拓展327·存量卡补题"),
    ("QB-1221", "什么是反比例关系？举一个生活中的例子。", "数学", "学科直答",
     ["反比例", "乘积一定", "速度", "时间"], "通识拓展327·存量卡补题"),
    ("QB-1222", "处方药和非处方药有什么区别？用药要注意什么？", "生活常识", "技术直答",
     ["说明书", "禁忌", "过期", "抗生素"], "通识拓展327·存量卡补题"),
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
    bank["version"] = "v5.97"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
