# -*- coding: utf-8 -*-
"""seed_common_192_cards.py · 通识拓展批次192知识卡+题库（幂等·两卡精批次）

192：生活常识-乙烯与水果催熟/生活常识-加湿器的卫生使用
KCCS 四要素+题干原句触发词。三重预检：乙烯在植物激素卡仅列举（催熟应用未
覆盖）、加湿器卫生（皮肤卡仅提湿度值）主题未覆盖；解冻肉命中厨房物理卡弃选。
执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ethyleneripe",
     "乙烯与水果催熟",
     "基础科学知识点内容（人话接口）", "化学",
     "**乙烯**是植物的「催熟激素」（气体激素）：水果成熟时自己释放乙烯，乙烯又"
     "**催熟自己与周围水果**（正反馈——一箱水果一颗烂/熟，整箱快速熟化）。**"
     "生活应用**：①**催熟**——把未熟的香蕉/猕猴桃/芒果与**苹果或熟香蕉**装"
     "入密封袋 1-3 天（苹果释放乙烯多），即可催熟；②**保鲜反向操作**——想"
     "延缓成熟就**隔离乙烯**：猕猴桃/香蕉分开装、别和苹果放一起；冷藏降温也"
     "减缓乙烯作用；③**乙烯吸收剂**（高锰酸钾保鲜剂）用于运输保鲜。**注意"
     "**：催熟的水果风味略逊树上熟（糖酸积累时间短）；柿子的涩味可用温水/与"
     "熟苹果同放脱涩。知识点：乙烯也是石化工业最重要的原料（塑料聚乙烯之源）"
     "——植物激素与工业原料同名不同物。",
     ["乙烯催熟水果", "苹果和香蕉放一起会怎样", "猕猴桃怎么催熟",
      "乙烯是什么", "水果保鲜隔绝乙烯"],
     ["问植物激素（用植物激素卡）", "问食品保鲜（用保鲜卡）"],
     "atomic", "",
     "乙烯=植物催熟激素（气体）：成熟水果释放乙烯正反馈催熟自己与邻居；催熟=与苹果/熟香蕉密封袋 1-3 天（猕猴桃香蕉芒果）；保鲜反向=隔离乙烯+冷藏；催熟风味略逊树上熟；工业乙烯=聚乙烯塑料原料同名不同物。"),
    ("kp_card_humidifier",
     "加湿器的卫生使用",
     "生活常识知识点内容（人话接口）", "生活常识",
     "加湿器用不对会「加病」：①**每天换水、每周彻底清洗**——水箱残水滋生细"
     "菌与霉菌，随水雾直接吸入肺（「加湿器肺炎」）；②**勿加自来水雾化**——自"
     "来水中的钙镁与消毒剂微粒随雾扩散（白粉沉淀+吸入刺激），用**纯净水**最"
     "稳；③**切勿往加湿器里加**消毒剂/精油/香水（韩国「加湿器杀菌剂事件」致"
     "数百人肺损伤死亡的教训——雾化吸入肺部的东西必须绝对安全）；④湿度控制"
     "**40-60%**（过高反促霉菌螨虫）；⑤超声雾化型最需要洁净水源，蒸发/无雾"
     "型相对耐受。特殊人群（婴儿/哮喘/免疫力低）尤其注意洁净。",
     ["加湿器怎么用才健康", "加湿器肺炎", "加湿器能加自来水吗",
      "加湿器加消毒剂", "加湿器湿度多少合适"],
     ["问冬季干燥（用皮肤干燥卡）", "问空气净化器"],
     "atomic", "",
     "加湿器卫生=每天换水每周彻底清洗（残水滋菌随雾入肺=加湿器肺炎）+用纯净水勿自来水（白粉与吸入刺激）+严禁加消毒剂精油（韩国杀菌剂事件数百人肺损伤）+湿度 40-60% 过高反促霉螨。"),
]

QUESTIONS = [
    ("QB-812", "乙烯为什么能催熟水果？想把未熟的猕猴桃快速催熟应该怎么做？", "化学", "技术直答",
     ["乙烯", "催熟激素", "苹果", "密封", "香蕉"], "通识拓展192"),
    ("QB-813", "加湿器使用不当会有什么健康风险？水箱应该怎么清洁？能加消毒剂吗？", "生活常识", "技术直答",
     ["换水", "清洗", "纯净水", "消毒剂", "肺", "40-60"], "通识拓展192"),
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
                               "level:L2", "status:verified", "batch:通识拓展192"],
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
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.65"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
