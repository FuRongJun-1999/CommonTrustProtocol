# -*- coding: utf-8 -*-
"""seed_common_281_cards.py · 通识拓展批次281·存量卡补题·清单中部（幂等）

281：5 张卡补 5 题（QB-1064~1068）——转录/RNA加工/三视图/反应级数/玻色爱因斯坦分布
     清单索引800起。预检已过（QB-1064~1068 可用）。
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
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA"}


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
    ("QB-1064", "转录的过程是什么？RNA聚合酶起什么作用？", "生物", "学科直答",
     ["转录", "RNA聚合酶", "模板", "启动子"], "通识拓展281·存量卡补题"),
    ("QB-1065", "mRNA转录后需要哪些加工修饰？可变剪接是什么？", "生物", "学科直答",
     ["加帽", "剪接", "内含子", "可变剪接"], "通识拓展281·存量卡补题"),
    ("QB-1066", "机械制图的三视图是哪三个？它们之间有什么对应关系？", "数学", "学科直答",
     ["主视图", "俯视图", "左视图", "长对正"], "通识拓展281·存量卡补题"),
    ("QB-1067", "一级反应和二级反应有什么区别？半衰期和浓度有什么关系？", "化学", "学科直答",
     ["一级反应", "二级", "半衰期", "浓度"], "通识拓展281·存量卡补题"),
    ("QB-1068", "玻色爱因斯坦分布适用于什么粒子？与费米分布有何不同？", "物理", "学科直答",
     ["玻色子", "分布", "泡利", "费米"], "通识拓展281·存量卡补题"),
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
    bank["version"] = "v5.52"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
