# -*- coding: utf-8 -*-
"""seed_common_283_cards.py · 通识拓展批次283·存量卡补题·清单中部（幂等）

283：5 张卡补 5 题（QB-1071~1075）——基尔霍夫定律/晶胞均摊法/超导电性/
     垄断竞争寡头/连接体问题
     清单索引900起。预检已过（QB-1071~1075 可用）。
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
    ("QB-1071", "基尔霍夫电流定律和电压定律分别是什么？", "物理", "学科直答",
     ["节点", "电流", "回路", "电压"], "通识拓展283·存量卡补题"),
    ("QB-1072", "什么是晶胞？晶胞中粒子的数目怎么用均摊法计算？", "化学", "学科直答",
     ["晶胞", "均摊", "顶点", "重复单元"], "通识拓展283·存量卡补题"),
    ("QB-1073", "超导体有什么特性？什么是迈斯纳效应？", "物理", "学科直答",
     ["超导", "零电阻", "抗磁", "迈斯纳"], "通识拓展283·存量卡补题"),
    ("QB-1074", "垄断竞争和寡头市场有什么特点？古诺模型是什么？", "数学", "学科直答",
     ["垄断竞争", "寡头", "古诺", "均衡"], "通识拓展283·存量卡补题"),
    ("QB-1075", "连接体问题怎么分析？整体法和隔离法分别什么时候用？", "物理", "学科直答",
     ["整体法", "隔离法", "加速度", "内力"], "通识拓展283·存量卡补题"),
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
    bank["version"] = "v5.54"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
