# -*- coding: utf-8 -*-
"""seed_common_267_cards.py · 通识拓展批次267·千题里程碑批次B（纯存量卡补题·幂等）

267：12 张卡补 12 题（QB-1005~1016），题库 988→1000 里程碑！
     幂级数/事务ACID/微积分基本定理/交变电流/彩票概率/送药讲究/大语言模型/
     三重积分/特征根法/信号转导/量子数/银器试毒
     预检已过（QB-1005~1016 可用）。
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
             "Durability", "CnnDNN"}


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
    ("QB-1005", "幂级数的收敛半径怎么求？收敛区间怎么确定？", "数学", "学科直答",
     ["收敛半径", "比值", "根值", "区间"], "通识拓展267·存量卡补题"),
    ("QB-1006", "数据库事务的ACID四大特性分别指什么？", "编程", "学科直答",
     ["原子性", "一致性", "隔离性", "持久性"], "通识拓展267·存量卡补题"),
    ("QB-1007", "微积分基本定理（牛顿莱布尼茨公式）的内容是什么？", "数学", "学科直答",
     ["牛顿", "莱布尼茨", "原函数", "积分"], "通识拓展267·存量卡补题"),
    ("QB-1008", "什么是交变电流？正弦交流电的瞬时值怎么表示？", "物理", "学科直答",
     ["周期性", "正弦", "峰值", "频率"], "通识拓展267·存量卡补题"),
    ("QB-1009", "中彩票头奖的概率是多少？买彩票能赚钱吗？", "生活常识", "技术直答",
     ["概率", "双色球", "返奖率", "期望"], "通识拓展267·存量卡补题"),
    ("QB-1010", "用什么送药最安全？西柚汁为什么不能和药一起吃？", "生活常识", "技术直答",
     ["温开水", "西柚汁", "牛奶", "茶"], "通识拓展267·存量卡补题"),
    ("QB-1011", "大语言模型是什么？它的基本架构和训练方式是什么？", "编程", "学科直答",
     ["Transformer", "预训练", "注意力", "参数"], "通识拓展267·存量卡补题"),
    ("QB-1012", "三重积分怎么计算？柱坐标和球坐标什么时候用？", "数学", "学科直答",
     ["三重积分", "直角坐标", "柱坐标", "球坐标"], "通识拓展267·存量卡补题"),
    ("QB-1013", "常系数线性微分方程怎么求解？特征根法是什么？", "数学", "学科直答",
     ["特征方程", "实根", "通解", "共轭"], "通识拓展267·存量卡补题"),
    ("QB-1014", "细胞信号转导的基本过程是什么？受体有哪些类型？", "生物", "学科直答",
     ["配体", "受体", "级联", "G蛋白"], "通识拓展267·存量卡补题"),
    ("QB-1015", "主量子数、角量子数、磁量子数分别决定什么？", "化学", "学科直答",
     ["主量子数", "能级", "角量子数", "磁量子数"], "通识拓展267·存量卡补题"),
    ("QB-1016", "银器试毒是真的吗？银针为什么会变黑？", "生活常识", "技术直答",
     ["银针", "砒霜", "硫", "硫化银"], "通识拓展267·存量卡补题"),
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
    bank["version"] = "v5.38"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
