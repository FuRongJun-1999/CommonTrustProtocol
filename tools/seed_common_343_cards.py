# -*- coding: utf-8 -*-
"""seed_common_343_cards.py · 通识拓展批次343·存量卡补题·清单中部（幂等）

343：4 张卡补 4 题（QB-1267~1270）——嫉妒陪伴/恶心照顾/挑选适配宠物/笔记方法
     清单索引2429-2525段。预检已过（QB-1267~1270 可用）。
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
    ("QB-1267", "看到别人比自己好感到嫉妒怎么办？", "生活咨询", "情感陪伴",
     ["嫉妒", "不平衡", "精力", "自己"], "通识拓展343·存量卡补题"),
    ("QB-1268", "感觉恶心想吐怎么办？要注意什么？", "生活常识", "技术直答",
     ["恶心", "温水", "休息", "吃坏"], "通识拓展343·存量卡补题"),
    ("QB-1269", "养宠物前应该考虑什么？怎么挑适合自己的宠物？", "生活咨询", "技术直答",
     ["时间", "预算", "住房", "性格"], "通识拓展343·存量卡补题"),
    ("QB-1270", "怎么做笔记才高效？为什么抄写是低效的？", "职场", "技术直答",
     ["自己的话", "结构", "不懂", "整理"], "通识拓展343·存量卡补题"),
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
    bank["version"] = "v6.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
