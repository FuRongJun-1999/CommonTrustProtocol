# -*- coding: utf-8 -*-
"""seed_common_295_cards.py · 通识拓展批次295·存量卡补题·清单中部（幂等）

295：5 张卡补 5 题（QB-1113~1117）——基本不等式/位移电流/合金/
     空间向量坐标/景观生态学
     清单索引1600起。预检已过（QB-1113~1117 可用）。
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
    ("QB-1113", "基本不等式的内容是什么？什么时候取等号？", "数学", "学科直答",
     ["基本不等式", "正数", "取等", "均"], "通识拓展295·存量卡补题"),
    ("QB-1114", "位移电流是什么？麦克斯韦为什么要补充它？", "物理", "学科直答",
     ["位移电流", "麦克斯韦", "安培环路", "守恒"], "通识拓展295·存量卡补题"),
    ("QB-1115", "合金和纯金属相比有什么特点？", "化学", "学科直答",
     ["合金", "硬度", "熔点", "耐腐蚀"], "通识拓展295·存量卡补题"),
    ("QB-1116", "空间向量的数量积怎么用坐标计算？", "数学", "学科直答",
     ["空间向量", "坐标", "数量积", "模"], "通识拓展295·存量卡补题"),
    ("QB-1117", "景观生态学的格局三要素是什么？什么是尺度效应？", "地理学", "学科直答",
     ["斑块", "廊道", "基质", "尺度"], "通识拓展295·存量卡补题"),
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
    bank["version"] = "v5.66"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
