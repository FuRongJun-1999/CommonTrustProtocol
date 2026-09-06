# -*- coding: utf-8 -*-
"""seed_common_266_cards.py · 通识拓展批次266·千题冲刺批次A（纯存量卡补题·幂等）

266：12 张卡补 12 题（QB-993~1004），题库 976→988（距千题差 12）：
     抽屉原理/熬夜补救/左撇子/谦辞敬辞/淀粉回生/绿豆汤变红/方便面/加湿器/
     细胞呼吸/免疫调节/诗经/二项分布
     卡已在库（触发词完整），零新卡。预检已过（QB-993~1004 可用）。
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP"}


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
    ("QB-993", "抽屉原理是什么？13 个人中为什么一定有两个人同月过生日？", "数学", "学科直答",
     ["抽屉", "鸽笼", "必有一个", "至少"], "通识拓展266·存量卡补题"),
    ("QB-994", "熬夜后怎么补救？第二天怎么恢复精神？", "生活常识", "技术直答",
     ["小睡", "20-30", "节律", "补水"], "通识拓展266·存量卡补题"),
    ("QB-995", "左撇子是怎么回事？左撇子更聪明吗？", "生活常识", "技术直答",
     ["10%", "偏侧化", "遗传", "矫正"], "通识拓展266·存量卡补题"),
    ("QB-996", "令尊和家父有什么区别？谦辞敬辞怎么用？", "语文", "学科直答",
     ["家父", "令尊", "谦辞", "敬辞"], "通识拓展266·存量卡补题"),
    ("QB-997", "馒头面包放久了为什么会变硬？怎么恢复松软？", "生活常识", "技术直答",
     ["淀粉", "回生", "结晶", "回蒸"], "通识拓展266·存量卡补题"),
    ("QB-998", "绿豆汤为什么煮着煮着变红了？怎么煮出绿色？", "生活常识", "技术直答",
     ["氧化", "碱性", "盖盖", "变红"], "通识拓展266·存量卡补题"),
    ("QB-999", "方便面防腐剂多吗？吃泡面对身体真的很不好吗？", "生活常识", "技术直答",
     ["防腐剂", "高钠", "营养", "辟谣"], "通识拓展266·存量卡补题"),
    ("QB-1000", "加湿器怎么用才健康？什么是「加湿器肺炎」？", "生活常识", "技术直答",
     ["换水", "清洗", "纯净水", "肺炎"], "通识拓展266·存量卡补题"),
    ("QB-1001", "细胞呼吸分几个阶段？有氧呼吸和无氧呼吸有什么区别？", "生物", "学科直答",
     ["有氧", "无氧", "线粒体", "乳酸"], "通识拓展266·存量卡补题"),
    ("QB-1002", "人体的三道防线是什么？体液免疫和细胞免疫有什么区别？", "生物", "学科直答",
     ["非特异性", "特异性", "抗体", "T细胞"], "通识拓展266·存量卡补题"),
    ("QB-1003", "《诗经》收录了多少篇诗歌？「六义」指什么？", "语文", "学科直答",
     ["305", "风", "雅", "颂"], "通识拓展266·存量卡补题"),
    ("QB-1004", "二项分布是什么？怎么计算成功k次的概率？", "数学", "学科直答",
     ["独立重复", "n次", "概率", "组合"], "通识拓展266·存量卡补题"),
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
    bank["version"] = "v5.37"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
