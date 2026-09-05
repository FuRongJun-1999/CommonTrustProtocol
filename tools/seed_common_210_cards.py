# -*- coding: utf-8 -*-
"""seed_common_210_cards.py · 通识拓展批次210知识卡+题库（幂等·两卡精批次）

210：生活技能-洗菜的正确方法/生活常识-大米的储存与米虫
KCCS 四要素+题干原句触发词。三重预检：洗菜与大储存双库零覆盖（geneeng 卡
为转基因角度、发芽土豆命中 foodsafety2 弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_washveg",
     "洗菜的正确方法",
     "生活常识知识点内容（人话接口）", "生活常识",
     "洗菜核心=**流动水冲洗为主，先洗后切**：①**流动水搓洗 30 秒以上**——机"
     "械冲刷是去除泥沙、大部分农残与病菌的主力（浸泡静水效果差、还会交叉污"
     "染）；②**先洗后切**——切开后清洗会让营养（水溶性维生素）从切口流失+"
     "污水渗入；③**辅助手段**：淡盐水/小苏打水泡 10 分钟（对部分农残有帮"
     "助），**勿用洗涤剂**（洗不净残留比农残更糟）；④特殊情况：包叶菜（白菜"
     "）剥掉外层叶片逐片冲、菌菇快速冲后现切现炒（久泡吸水影响口感）、贝类"
     "吐沙加盐加油静置。**洗不掉的怎么办**——农药残留国标本身留有安全余量，"
     "烹调加热还会进一步分解，不必过度焦虑。",
     ["洗菜的正确方法", "洗菜用盐水还是清水", "先洗后切为什么",
      "蔬菜怎么洗农药残留", "洗菜要泡多久"],
     ["问食品标签（用标签卡）", "问焯水（烹饪）"],
     "atomic", "",
     "洗菜=流动水搓洗 30 秒以上为主力+先洗后切（切后洗营养流失污水渗入）+淡盐水小苏打辅助 10 分钟+勿用洗涤剂；包叶菜逐片冲/菌菇快冲/贝类吐沙；国标农残有安全余量+加热分解，不过度焦虑。"),
    ("kp_card_ricestore",
     "大米的储存与米虫",
     "生活常识知识点内容（人话接口）", "生活常识",
     "大米储存三敌=**潮湿、高温、虫卵**：①**密封**——米桶/密封罐（防潮防虫"
     "卵进入）；②**阴凉避光**——高温加速米粒油脂酸败（哈喇味）、阳光直射升"
     "温生虫；③**天然驱虫**——米袋中放几瓣大蒜/花椒包（气味驱避米虫）；④**"
     "已生虫**——放阴凉处等虫爬出筛除，或**冷冻 24 小时**（-18°C 杀死虫与"
     "卵，筛后再吃——虫不产生毒素，筛净可食）；**勿暴晒**（暴晒让米粒开裂碎"
     "裂+口感变差，还「晒醒」虫卵加速繁殖）。**买米原则**：小袋多次购买优于"
     "大袋囤积（开封后 2-3 个月吃完口感营养最佳）。",
     ["大米怎么储存不生虫", "大米生了虫还能吃吗", "米虫怎么来的",
      "大米能暴晒吗", "大米放大蒜花椒", "密封米桶"],
     ["问面粉储存", "问粮食安全"],
     "atomic", "",
     "大米储存三敌=潮湿高温虫卵：密封罐+阴凉避光+大蒜花椒驱虫；生虫=冷冻 24h 杀虫筛后可食（虫无毒）勿暴晒（碎裂口感差还醒虫）；小袋多次买开封 2-3 月吃完最佳。"),
]

QUESTIONS = [
    ("QB-845", "洗菜为什么要「先洗后切」？用什么水洗菜去除农残效果更好？", "生活常识", "技术直答",
     ["流动水", "先洗后切", "营养", "流失", "小苏打", "洗涤剂"], "通识拓展210"),
    ("QB-846", "大米生了米虫还能吃吗？怎么储存大米防止生虫？", "生活常识", "技术直答",
     ["冷冻", "筛除", "可食", "密封", "阴凉", "花椒", "大蒜"], "通识拓展210"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


def ensure_seed() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    inserted = updated = skipped = 0
    for nid, name, domain, dgroup, content, conds, negs, ktype, sub_route, direct in NODES:
        sa = {
            "name": name,
            "kind": "knowledge_point",
            "knowledge_type": ktype,
            "sub_route": sub_route,
            "domain": domain,
            "domain_group": dgroup,
            "edu_level": "",
            "comment": {
                "name": f"{name}（{dgroup}·通识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——通识高频问题知识条目",
                "执行": direct or content,
                "不适用条件": negs,
            },
        }
        payload = json.dumps(sa, ensure_ascii=False)
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if row and isinstance(row[0], str) and row[0] == payload:
            skipped += 1
            continue
        if not row:
            tags = json.dumps(["knowledge_point", f"domain:{domain}",
                               "level:L2", "status:verified", "batch:通识拓展210"],
                              ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, tags, importance,"
                " confidence, layer, state_attributes, created_at,"
                " spatial_coordinates, temporal_coordinate, condition_space,"
                " semantic_coordinates) VALUES "
                "(?,?,?,?,?,?,?,?," + "CAST(strftime('%s','now') AS INTEGER),"
                 "'[]', '[0,0,0]', '{}', '{}')",
                (nid, content, "text", tags, 0.8, 1.0, "knowledge", payload))
            inserted += 1
        else:
            cur.execute("UPDATE nodes SET state_attributes=?, content=?, "
                        "created_at=CAST(strftime('%s','now') AS INTEGER) "
                        "WHERE id=?", (payload, content, nid))
            updated += 1
    conn.commit()
    conn.close()

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.82"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
