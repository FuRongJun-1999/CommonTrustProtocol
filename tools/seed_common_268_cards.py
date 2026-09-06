# -*- coding: utf-8 -*-
"""seed_common_268_cards.py · 通识拓展批次268·存量卡补题（幂等）

268：7 张卡补 7 题（QB-1017~1023）——格林公式/最大流最小割/泊松括号/深度学习/
     细胞增殖/一阶微分方程/明清小说
     预检已过（QB-1017~1023 可用；擦伤已有 QB-891 跳过清单误报）。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "Atomicity", "Consistency", "Isolation",
             "Durability", "CNN", "RNN", "LSTM", "Ford", "Fulkerson",
             "Edmonds", "Karp", "Dinic"}


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
    ("QB-1017", "格林公式的内容是什么？使用条件是什么？", "数学", "学科直答",
     ["曲线积分", "二重积分", "闭曲线", "条件"], "通识拓展268·存量卡补题"),
    ("QB-1018", "最大流最小割定理是什么？常见算法有哪些？", "编程", "学科直答",
     ["最大流", "最小割", "增广路径", "算法"], "通识拓展268·存量卡补题"),
    ("QB-1019", "泊松括号的定义是什么？它在力学中有什么用？", "物理", "学科直答",
     ["泊松括号", "正则", "守恒量", "力学"], "通识拓展268·存量卡补题"),
    ("QB-1020", "深度学习常用网络结构有哪些？各适合什么任务？", "编程", "学科直答",
     ["CNN", "图像", "RNN", "序列"], "通识拓展268·存量卡补题"),
    ("QB-1021", "细胞分裂有哪几种方式？有丝分裂的过程分哪几个时期？", "生物", "学科直答",
     ["有丝分裂", "减数分裂", "间期", "DNA"], "通识拓展268·存量卡补题"),
    ("QB-1022", "一阶微分方程有哪些常见解法？什么是可分离变量方程？", "数学", "学科直答",
     ["一阶", "分离变量", "通解", "常数"], "通识拓展268·存量卡补题"),
    ("QB-1023", "明清四大名著分别是哪几部？作者是谁？各是什么题材？", "语文", "学科直答",
     ["三国演义", "水浒传", "西游记", "红楼梦"], "通识拓展268·存量卡补题"),
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
    bank["version"] = "v5.39"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
