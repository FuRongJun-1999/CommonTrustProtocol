# -*- coding: utf-8 -*-
"""seed_common_287_cards.py · 通识拓展批次287·存量卡补题·清单中部（幂等）

287：5 张卡补 5 题（QB-1085~1089）——博弈论初步/动生感生电动势/镧系锕系/
     企业文化/电源等效
     清单索引1150起。预检已过（QB-1085~1089 可用）。
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
    ("QB-1085", "囚徒困境说明了什么？什么是纳什均衡？", "数学", "学科直答",
     ["囚徒困境", "占优策略", "纳什均衡", "博弈"], "通识拓展287·存量卡补题"),
    ("QB-1086", "动生电动势和感生电动势有什么区别？", "物理", "学科直答",
     ["动生", "感生", "切割", "涡旋电场"], "通识拓展287·存量卡补题"),
    ("QB-1087", "镧系元素有什么特点？什么是镧系收缩？", "化学", "学科直答",
     ["镧系", "收缩", "稀土", "锕系"], "通识拓展287·存量卡补题"),
    ("QB-1088", "企业文化包含哪些层次？它有什么作用？", "职场", "学科直答",
     ["价值观", "符号", "制度", "层次"], "通识拓展287·存量卡补题"),
    ("QB-1089", "电压源和电流源怎么等效变换？理想电压源能短路吗？", "物理", "学科直答",
     ["电压源", "电流源", "等效", "短路"], "通识拓展287·存量卡补题"),
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
    bank["version"] = "v5.58"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
