# -*- coding: utf-8 -*-
"""seed_common_109_cards.py · 通识拓展批次109知识卡+题库（幂等）

109：物理学-蒸汽烫伤为何更严重/化学-金属与氧气反应/生物学-生态系统的类型
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_steamscald",
     "蒸汽烫伤为什么比开水更严重",
     "基础科学知识点内容（人话接口）", "物理学",
     "100℃ 的水蒸气烫伤比 100℃ 的开水更严重——因为水蒸气接触皮肤时先**液化**"
     "（气→水），液化**放出大量热**（每克水蒸气液化放热约 2260J，相当于同量开水"
     "再升 200 多度才释放的热量），然后 100℃ 的水才继续烫伤——多了一个液化放热"
     "环节。急救：立即用流动冷水冲 15-30 分钟（带走热量），不涂牙膏酱油（易感染"
     "且妨碍散热），严重者剪开衣物送医。同类：被 100℃ 水蒸气灼伤>100℃ 开水>60"
     "℃ 热水长时间接触——温度+作用时间+是否液化放热共同决定伤害程度。",
     ["蒸汽烫伤为什么比开水更严重", "液化放热", "烫伤了怎么办",
      "水蒸气液化放出多少热", "烫伤后能涂牙膏吗", "烫伤急救步骤"],
     ["问烧伤面积九分法", "问低温烫伤"],
     "atomic", "",
     "蒸汽烫伤更重=多一个液化放热环节(1g 水汽液化放 2260J)；急救=冷水冲 15-30min·不涂牙膏酱油·重症送医；伤害=温度+时间+液化放热共同决定。"),
    ("kp_card_metalO2",
     "金属与氧气的反应",
     "基础科学知识点内容（人话接口）", "化学",
     "金属与氧气反应的现象差异体现活动性强弱：①镁——剧烈燃烧，发出耀眼白光（常"
     "做照明弹/烟花）；②铁——在空气中不能燃烧，但在**纯氧中剧烈燃烧、火星四"
     "射**，生成黑色固体四氧化三铁（Fe₃O₄）——集气瓶底要放少量水或细沙（防熔融"
     "物炸裂瓶底）；③铜——加热变黑（生成氧化铜）；④金——即使在高温下也不与氧"
     "气反应（「真金不怕火炼」）。活动性顺序即：镁＞铁＞铜＞金。铁生锈是缓慢氧化"
     "（rust 呼应）——同样是与氧气反应，快慢不同。",
     ["铁在氧气中燃烧的现象", "镁条燃烧的现象", "真金不怕火炼的原因",
      "铁丝在氧气中燃烧瓶底为什么要放水", "金属与氧气反应的活动性", "四氧化三铁"],
     ["问燃烧与缓慢氧化对比", "问金属活动性顺序复习"],
     "atomic", "",
     "金属+氧气现象差=活动性差异：镁白光剧烈燃/铁纯氧中火星四射生成 Fe₃O₄(瓶底放水防炸裂)/铜加热变黑/金不反应（真金不怕火炼）——镁＞铁＞铜＞金。"),
    ("kp_card_ecotypes",
     "生态系统的类型",
     "基础科学知识点内容（人话接口）", "生物学",
     "生态系统类型（bio 圈内的分层拼图）：自然生态系统——①森林（「地球之肺」，"
     "物种最丰富）；②草原；③海洋（地球最大生态系统）；④淡水（湖泊河流）；⑤湿"
     "地（「地球之肾」——净化水质蓄洪防旱，如扎龙丹顶鹤保护区）；⑥荒漠、苔原。"
     "人工生态系统——农田、城市（人是核心，依赖其他系统供给）。共同规律：都由生"
     "物部分+非生物部分构成，都存在物质循环和能量流动。生物圈是最大的生态系统。"
     "保护优先级：湿地与森林锐减是全球生态三大危机之一（与生物多样性下降、气候"
     "变化并列）。",
     ["生态系统的类型有哪些", "地球之肾是什么", "地球之肺是什么",
      "最大的生态系统是什么", "农田和城市生态系统的特点", "湿地的作用"],
     ["问生物圈范围复习", "问湿地退化案例"],
     "atomic", "",
     "类型=自然(森林肺/草原/海洋最大/淡水/湿地肾/荒漠)+人工(农田·城市人核心)；共性=生物+非生物·物质循环能量流动；生物圈=最大。"),
]

QUESTIONS = [
    ("QB-572", "蒸汽烫伤为什么比开水更严重", "物理学", "技术直答",
     ["液化", "放热"], "通识拓展109"),
    ("QB-573", "铁在氧气中燃烧的现象", "化学", "技术直答",
     ["火星四射", "四氧化三铁"], "通识拓展109"),
    ("QB-574", "生态系统的类型有哪些", "生物学", "技术直答",
     ["森林", "草原", "海洋", "湿地"], "通识拓展109"),
]


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
                               "level:L2", "status:verified", "batch:通识拓展109"],
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
    bank["version"] = "v2.1"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
