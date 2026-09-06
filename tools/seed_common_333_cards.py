# -*- coding: utf-8 -*-
"""seed_common_333_cards.py · 通识拓展批次333·存量卡补题·清单中部（幂等）

333：4 张卡补 4 题（QB-1237~1240）——分式方程/锕系元素/行程问题/古诗词鉴赏
     清单索引2290-2310段。预检已过（QB-1237~1240 可用）。
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
    ("QB-1237", "什么是分式方程？解分式方程为什么要检验？", "数学", "学科直答",
     ["分母", "未知数", "整式方程", "增根"], "通识拓展333·存量卡补题"),
    ("QB-1238", "锕系元素有什么特点？核燃料用的是哪些元素？", "化学", "学科直答",
     ["锕系", "放射性", "铀", "钚"], "通识拓展333·存量卡补题"),
    ("QB-1239", "行程问题的基本公式是什么？相向而行和同向而行怎么区分？",
     "数学", "学科直答",
     ["速度", "时间", "路程", "相向"], "通识拓展333·存量卡补题"),
    ("QB-1240", "鉴赏古诗词可以从哪些角度入手？什么是意象和意境？", "语文", "学科直答",
     ["意象", "意境", "炼字", "手法"], "通识拓展333·存量卡补题"),
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
    bank["version"] = "v6.03"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
