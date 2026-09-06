# -*- coding: utf-8 -*-
"""seed_common_347_cards.py · 通识拓展批次347·存量卡补题·清单中部（幂等）

347：4 张卡补 4 题（QB-1279~1282）——先天性行为/孤独陪伴/发烧应对/
     挑选宠物综合考量
     清单索引2460-2525段。预检已过（QB-1279~1282 可用）。
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
    ("QB-1279", "什么是动物的先天性行为？蜘蛛结网是学出来的吗？", "生物", "学科直答",
     ["先天性", "遗传", "蜘蛛", "生来"], "通识拓展347·存量卡补题"),
    ("QB-1280", "什么是课题学习？它有什么用处？", "数学", "学科直答",
     ["课题", "综合运用", "探究", "合作"], "通识拓展347·存量卡补题"),
    ("QB-1281", "感到孤独怎么办？怎么缓解孤独感？", "生活咨询", "情感陪伴",
     ["孤独", "联结", "电话", "正常"], "通识拓展341·存量卡补题"),
    ("QB-1282", "发烧了该怎么办？什么时候要去看医生？", "生活常识", "技术直答",
     ["体温", "多喝水", "休息", "就医"], "通识拓展347·存量卡补题"),
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
    bank["version"] = "v6.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
