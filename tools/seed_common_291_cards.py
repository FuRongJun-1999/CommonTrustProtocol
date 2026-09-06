# -*- coding: utf-8 -*-
"""seed_common_291_cards.py · 通识拓展批次291·存量卡补题·清单中部（幂等）

291：5 张卡补 5 题（QB-1099~1103）——硅及其化合物/碱金属/分治策略/
     两次世界大战/质量单位
     清单索引1400起。预检已过（QB-1099~1103 可用）。
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
    ("QB-1099", "二氧化硅有什么用途？氢氟酸为什么能雕刻玻璃？", "化学", "学科直答",
     ["二氧化硅", "光导纤维", "氢氟酸", "雕刻"], "通识拓展291·存量卡补题"),
    ("QB-1100", "碱金属为什么最活泼？钠与水反应有什么现象？", "化学", "学科直答",
     ["碱金属", "活泼", "钠", "水反应"], "通识拓展291·存量卡补题"),
    ("QB-1101", "分治策略的三步是什么？归并排序为什么体现分治？", "编程", "学科直答",
     ["分解", "递归", "合并", "归并"], "通识拓展291·存量卡补题"),
    ("QB-1102", "两次世界大战分别发生在什么时间？一战后的凡尔赛体系是什么？",
     "历史", "学科直答",
     ["一战", "二战", "凡尔赛", "反法西斯"], "通识拓展291·存量卡补题"),
    ("QB-1103", "克、千克、吨之间怎么换算？", "数学", "学科直答",
     ["克", "千克", "吨", "1000"], "通识拓展291·存量卡补题"),
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
    bank["version"] = "v5.62"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
