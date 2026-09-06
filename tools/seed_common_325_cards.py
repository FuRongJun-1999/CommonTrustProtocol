# -*- coding: utf-8 -*-
"""seed_common_325_cards.py · 通识拓展批次325·存量卡补题·清单中部（幂等）

325：4 张卡补 4 题（QB-1213~1216）——口语表达/难过陪伴/众数/电荷
     清单索引2410-2440段。预检已过（QB-1213~1216 可用）。
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
    ("QB-1213", "高中口语表达有哪些训练形式？口语表达要注意什么？", "语文", "学科直答",
     ["话题讨论", "观点陈述", "即兴演讲", "逻辑"], "通识拓展325·存量卡补题"),
    ("QB-1214", "难过的情绪来了怎么办？怎么让自己好受一些？", "生活咨询", "情感陪伴",
     ["难过", "哭", "说话", "过去"], "通识拓展325·存量卡补题"),
    ("QB-1215", "什么是众数？众数可以有几个？", "数学", "学科直答",
     ["众数", "次数最多", "不止一个", "集中趋势"], "通识拓展325·存量卡补题"),
    ("QB-1216", "电荷有几种？电荷之间相互作用有什么规律？", "物理", "学科直答",
     ["正负", "同种相斥", "异种相吸", "电荷量"], "通识拓展325·存量卡补题"),
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
    bank["version"] = "v5.95"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
