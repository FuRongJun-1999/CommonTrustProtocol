# -*- coding: utf-8 -*-
"""seed_common_305_cards.py · 通识拓展批次305·存量卡补题·清单中部（幂等）

305：5 张卡补 5 题（QB-1145~1149）——流体压强/平行判定性质/依法维权/
     岩石与土壤/写日记
     清单索引2100起。预检已过（QB-1145~1149 可用）。
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
    ("QB-1145", "流体压强与流速有什么关系？举个生活中的例子。", "物理", "学科直答",
     ["流速", "压强", "伯努利", "升力"], "通识拓展305·存量卡补题"),
    ("QB-1146", "线面平行的判定定理是什么？面面平行怎么判定？", "数学", "学科直答",
     ["线面平行", "面面平行", "判定", "相交直线"], "通识拓展305·存量卡补题"),
    ("QB-1147", "遇到侵权怎么依法维权？维权的途径有哪些？", "生活常识", "技术直答",
     ["协商", "调解", "仲裁", "诉讼"], "通识拓展305·存量卡补题"),
    ("QB-1148", "岩石和土壤有什么关系？土壤为什么能种植物？", "基础科学", "学科直答",
     ["岩石", "土壤", "风化", "植物"], "通识拓展305·存量卡补题"),
    ("QB-1149", "日记的格式是什么？写日记有什么好处？", "语文", "学科直答",
     ["日期", "天气", "正文", "真话"], "通识拓展305·存量卡补题"),
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
    bank["version"] = "v5.75"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
