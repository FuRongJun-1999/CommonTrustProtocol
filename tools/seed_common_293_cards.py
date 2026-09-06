# -*- coding: utf-8 -*-
"""seed_common_293_cards.py · 通识拓展批次293·存量卡补题·清单中部（幂等）

293：5 张卡补 5 题（QB-1106~1110）——电势/线性时间排序/生态学概念/
     茅盾左翼文学/产品策略
     清单索引1500起。预检已过（QB-1106~1110 可用）。
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
    ("QB-1106", "电势是什么？电势沿电场线方向怎么变化？", "物理", "学科直答",
     ["电势", "标量", "电场线", "降低"], "通识拓展293·存量卡补题"),
    ("QB-1107", "计数排序、基数排序、桶排序为什么能突破比较排序的下限？",
     "编程", "学科直答",
     ["计数", "基数", "桶", "非比较"], "通识拓展293·存量卡补题"),
    ("QB-1108", "生态学的研究层次有哪些？种群和群落有什么区别？", "生物", "学科直答",
     ["个体", "种群", "群落", "生态系统"], "通识拓展293·存量卡补题"),
    ("QB-1109", "茅盾的《子夜》写了什么？左翼作家联盟是什么？", "语文", "学科直答",
     ["茅盾", "子夜", "左翼", "民族工业"], "通识拓展293·存量卡补题"),
    ("QB-1110", "产品整体概念分哪三个层次？产品生命周期分哪几个阶段？", "职场", "学科直答",
     ["核心利益", "附加产品", "生命周期", "引入"], "通识拓展293·存量卡补题"),
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
    bank["version"] = "v5.64"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
