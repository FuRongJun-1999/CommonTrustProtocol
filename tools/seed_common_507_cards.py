# -*- coding: utf-8 -*-
"""seed_common_507_cards.py · 通识拓展批次507知识卡+题库（幂等）

507：3 张存量卡补题·童话寓言域深化
    （伊索篇目道理 kp_card_aesop / 海的女儿辨析+卖火柴小女孩
    kp_card_andersen——角度与 QB-1607/1672/1673 概述题不重复；
    守株待兔 QB-111、成语来源 QB-1483 已覆盖跳过）。
预检已过（QB-1753~1755 可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


QUESTIONS = [
    ("QB-1753", "《狼来了》和《农夫与蛇》出自哪部寓言集？各讲什么道理？",
     "文学常识", "技术直答",
     ["狼来了", "农夫与蛇", "伊索寓言", "道理"], "通识拓展507·存量补题"),
    ("QB-1754", "《海的女儿》是格林童话还是安徒生童话？讲了什么故事？",
     "文学常识", "技术直答",
     ["海的女儿", "安徒生", "人鱼", "小美人鱼"], "通识拓展507·存量补题"),
    ("QB-1755", "《卖火柴的小女孩》讲了什么故事？为什么感人？",
     "文学常识", "技术直答",
     ["卖火柴的小女孩", "安徒生", "火柴", "幻象"], "通识拓展507·存量补题"),
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
    bank["version"] = "v7.72"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
