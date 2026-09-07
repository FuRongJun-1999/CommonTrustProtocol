# -*- coding: utf-8 -*-
"""seed_common_378_cards.py · 通识拓展批次378·存量卡补题（幂等）

378：3 张卡补 3 题（QB-1372~1374）——强度理论/支持向量机/平衡常数与温度
     清单索引400段取卡（原候选微波背景/酶学/高斯定理已有题被程序化
     过滤排除）。预检已过（QB-1372~1374 可用，三主题题库 0 覆盖）。
     （本批次号曾被困倦睡眠重复题占用，2026-09-07 重写为真实新题。）
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("QB-1372", "材料力学中的四个强度理论是什么？脆性和塑性材料分别怎么选？",
     "材料力学", "技术直答",
     ["强度理论", "脆性", "塑性", "失效"], "通识拓展378·存量卡补题"),
    ("QB-1373", "什么是支持向量机？支持向量指的是什么？",
     "机器学习", "技术直答",
     ["支持向量机", "SVM", "间隔", "支持向量"], "通识拓展378·存量卡补题"),
    ("QB-1374", "温度变化对化学平衡有什么影响？范特霍夫方程说明什么？",
     "物理化学", "技术直答",
     ["平衡常数", "温度", "范特霍夫", "吸热"], "通识拓展378·存量卡补题"),
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
    bank["version"] = "v6.48"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
