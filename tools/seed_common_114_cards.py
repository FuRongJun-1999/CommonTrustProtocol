# -*- coding: utf-8 -*-
"""seed_common_114_cards.py · 通识拓展批次114知识卡+题库（幂等）

114：物理学-家电能效标识/生物学-无脊椎动物的主要类群
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_energylabel",
     "家电能效标识",
     "基础科学知识点内容（人话接口）", "物理学",
     "中国能效标识分五级（1 级最节能）：一级能效最高（国际先进水平）、二级节"
     "能、三级为市场准入门槛（普遍水平）、四五级逐步淘汰。能效标识还标注耗电量"
     "（如冰箱 24 小时耗电度数）与关键性能参数。选购建议：使用频繁的电器（冰"
     "箱/空调）选一级——虽然贵但长期电费省得多；使用少的电器可选二级三级。节能"
     "细节：变频空调比定频省电（达到设定温度后低功率维持）；一级能效空调比五级"
     "省电 30% 以上。国家能效「领跑者」制度：推选市面最节能产品引导行业升级。"
     "节电计算：1000W 电器开 1 小时=1 度电，若每天少开 2 小时空调（1500W），一年"
     "夏季节电约 270 度。",
     ["家电能效标识分几级", "一级能效和三级能效差多少", "变频空调为什么省电",
      "怎么选购节能电器", "能效标识上有什么信息", "什么是一级能效"],
     ["问能效标准演进", "问电器待机耗电实测"],
     "atomic", "",
     "中国能效标识五级（1 级最节能·3 级=准入门槛）：频繁使用的冰箱空调选一级长期省电费；变频空调低功率维持省电 30%+；1000W×1h=1 度电。"),
    ("kp_card_invertebrate",
     "无脊椎动物的主要类群",
     "基础科学知识点内容（人话接口）", "生物学",
     "无脊椎动物约占动物种数 95%，主要类群（由简单到复杂）：①腔肠动物——刺细"
     "胞+辐射对称（水螅/海葵/珊瑚虫/水母）；②扁形动物——背腹扁平、左右对称（涡"
     "虫/猪肉绦虫/血吸虫）；③线形动物——身体细长圆柱（蛔虫/蛲虫/钩虫）；④环节动"
     "物——身体由相似体节构成（蚯蚓/水蛭/沙蚕）；⑤软体动物——柔软身体+外套膜，"
     "大多有贝壳（河蚌/蜗牛/乌贼/章鱼）；⑥节肢动物——种类最多（占动物 2/3 以"
     "上），体表有外骨骼、身体和附肢分节：昆虫纲（三对足两对翅）、蛛形纲（蜘"
     "蛛蝎）、多足纲（蜈蚣）、甲壳纲（虾蟹）。环节/软体/节肢并称「无脊椎三大繁"
     "荣」。无脊椎动物没有脊椎骨组成的脊柱——这是与脊椎动物（鱼两栖爬鸟哺乳）"
     "的根本区别。",
     ["无脊椎动物有哪些主要类群", "节肢动物为什么种类最多", "蚯蚓属于什么动物",
      "无脊椎动物和脊椎动物的根本区别", "昆虫和蜘蛛的区别", "珊瑚虫属于什么动物"],
     ["问昆虫纲特征复习", "问各类群代表动物表"],
     "atomic", "",
     "无脊椎六类（简→繁）：腔肠(水螅)→扁形(绦虫)→线形(蛔虫)→环节(蚯蚓)→软体(蚌螺章鱼)→节肢(占 2/3·昆虫蛛蝎蜈蚣虾蟹)；无脊柱；昆虫三对足两对翅。"),
]

QUESTIONS = [
    ("QB-590", "家电能效标识分几级", "物理学", "技术直答",
     ["五级", "1级"], "通识拓展114"),
    ("QB-591", "无脊椎动物有哪些主要类群", "生物学", "技术直答",
     ["腔肠", "扁形", "线形", "环节", "软体", "节肢"], "通识拓展114"),
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
                               "level:L2", "status:verified", "batch:通识拓展114"],
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
    bank["version"] = "v2.6"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
