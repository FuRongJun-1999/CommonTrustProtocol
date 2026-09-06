# -*- coding: utf-8 -*-
"""seed_common_273_cards.py · 通识拓展批次273·存量卡补题·清单中部（幂等）

273：6 张学术卡补 6 题（QB-1036~1041）——细胞衰老凋亡/微波背景/酶学基础/
     高斯定理/平衡常数与温度/氢原子精确解
     清单索引400起。预检已过（QB-1036~1041 可用）。
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
             "FADH2", "Vmax", "Km"}


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
    ("QB-1036", "细胞衰老有什么特征？细胞凋亡和细胞坏死有什么区别？", "生物", "学科直答",
     ["衰老", "凋亡", "程序性", "坏死"], "通识拓展273·存量卡补题"),
    ("QB-1037", "宇宙微波背景辐射是什么？它为什么能证明大爆炸理论？", "物理", "学科直答",
     ["微波背景", "遗迹", "2.7K", "大爆炸"], "通识拓展273·存量卡补题"),
    ("QB-1038", "酶为什么能加速化学反应？米氏方程描述什么关系？", "生物", "学科直答",
     ["催化剂", "活化能", "米氏方程", "底物"], "通识拓展273·存量卡补题"),
    ("QB-1039", "高斯定理的内容是什么？什么情况下用它求电场最方便？", "物理", "学科直答",
     ["电通量", "闭合曲面", "电荷", "对称"], "通识拓展273·存量卡补题"),
    ("QB-1040", "温度升高化学平衡怎么移动？范特霍夫方程说明什么？", "化学", "学科直答",
     ["平衡常数", "温度", "吸热", "放热"], "通识拓展273·存量卡补题"),
    ("QB-1041", "氢原子的薛定谔方程怎么解？三个量子数各决定什么？", "物理", "学科直答",
     ["薛定谔方程", "波函数", "量子数", "能级"], "通识拓展273·存量卡补题"),
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
    bank["version"] = "v5.44"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
