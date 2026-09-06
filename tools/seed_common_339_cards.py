# -*- coding: utf-8 -*-
"""seed_common_339_cards.py · 通识拓展批次339·存量卡补题·清单中部（幂等）

339：4 张卡补 4 题（QB-1255~1258）——弹力/议论文写作/语用题/英语学习习惯
     清单索引2360-2390段。预检已过（QB-1255~1258 可用）。
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
    ("QB-1255", "什么是弹力？弹簧和皮筋为什么能弹回来？", "物理", "学科直答",
     ["弹力", "形变", "弹簧", "恢复"], "通识拓展339·存量卡补题"),
    ("QB-1256", "议论文写作有什么要求？怎么让论证更有力？", "语文", "学科直答",
     ["观点", "论据", "论证", "思辨"], "通识拓展339·存量卡补题"),
    ("QB-1257", "语用题有哪些常见题型？考查什么能力？", "语文", "学科直答",
     ["词语辨析", "病句", "仿写", "压缩"], "通识拓展339·存量卡补题"),
    ("QB-1258", "英语学习要养成哪些好习惯？", "语文", "学科直答",
     ["听读", "开口", "词汇", "词典"], "通识拓展339·存量卡补题"),
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
    bank["version"] = "v6.08"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
