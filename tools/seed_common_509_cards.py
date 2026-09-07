# -*- coding: utf-8 -*-
"""seed_common_509_cards.py · 通识拓展批次509知识卡+题库（幂等）

509：3 张存量卡补题·元曲域一次补满（挂元曲卡 kp_6572868858——
    四大家与窦娥冤/西厢记/天净沙秋思；宋词 QB-1083/1549/1550、
    丝路 QB-136/159/1685 已覆盖程序化跳过）。
预检已过（QB-1759~1761 可用，关汉卿/窦娥冤/西厢记题库零题）。
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
    ("QB-1759", "元曲四大家是谁？《窦娥冤》讲了什么故事？",
     "文学常识", "技术直答",
     ["元曲四大家", "关汉卿", "窦娥冤", "六月飞雪"], "通识拓展509·存量补题"),
    ("QB-1760", "《西厢记》讲了什么故事？「愿天下有情人终成眷属」出自哪里？",
     "文学常识", "技术直答",
     ["西厢记", "王实甫", "崔莺莺", "红娘"], "通识拓展509·存量补题"),
    ("QB-1761", "《天净沙·秋思》是谁的作品？「枯藤老树昏鸦」描绘了什么？",
     "文学常识", "技术直答",
     ["天净沙", "马致远", "秋思", "断肠人"], "通识拓展509·存量补题"),
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
    bank["version"] = "v7.74"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
