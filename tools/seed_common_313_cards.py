# -*- coding: utf-8 -*-
"""seed_common_313_cards.py · 通识拓展批次313·存量卡补题·清单尾部（幂等）

313：4 张卡补 4 题（QB-1171~1174）——疼痛提示/经济与社会生活/祖国山河/代数式
     清单尾部（索引2450起）。预检已过（QB-1171~1174 可用）。
     注意：名篇背诵×2、经济与社会生活×2、祖国山河×2 等重复卡只补一次。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("QB-1171", "身体疼是在提醒什么？什么时候该看医生？", "生活咨询", "情感陪伴",
     ["疼", "警告", "休息", "看医生"], "通识拓展313·存量卡补题"),
    ("QB-1172", "选择性必修《经济与社会生活》覆盖哪些主题？", "历史", "学科直答",
     ["食物生产", "商业贸易", "交通", "医疗"], "通识拓展313·存量卡补题"),
    ("QB-1173", "中国疆域有什么特点？为什么要了解祖国山河？", "地理学", "学科直答",
     ["疆域", "辽阔", "山河", "名胜"], "通识拓展313·存量卡补题"),
    ("QB-1174", "什么是代数式？代数式的值由什么决定？", "数学", "学科直答",
     ["代数式", "运算符号", "字母", "取值"], "通识拓展313·存量卡补题"),
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
    bank["version"] = "v5.83"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
