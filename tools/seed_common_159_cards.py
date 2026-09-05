# -*- coding: utf-8 -*-
"""seed_common_159_cards.py · 通识拓展批次159知识卡+题库（幂等·两卡精批次）

159：历史学-李时珍与《本草纲目》/生活常识-泡茶水温与冲泡
KCCS 四要素+题干原句触发词。三重预检：李时珍双库零覆盖；泡茶在 teaculture
卡「不适用条件」中显式划界（分类历史 vs 冲泡实操）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_lishizhen",
     "李时珍与《本草纲目》",
     "人文通识知识点内容（人话接口）", "历史学",
     "李时珍（1518-1593，明代湖北蕲州人）：出身医药世家，三次乡试不第弃科举从"
     "医——因医术入太医院。发现历代「本草」（药物学著作）谬误不少（把同一药"
     "物当成两种、毒性搞反等），遂立志重修：**历时约 27 年**（1552-1578 编"
     "撰），走遍大江南北采药访民（亲尝草药辨真伪），三易其稿，著成《**本草纲"
     "目**》：全书约 **190 万字、52 卷**，载药 **1892 种**（新增 374 种）、附"
     "方 **11096 首**、插图千余幅——首创**分类体系**（矿物→植物→动物由低到"
     "高，含「释名/气味/主治/发明」诸项），是古代最系统的博物学巨著。**影响**"
     "：先后译成拉丁/英/法/德/日等多国文字——**达尔文**在著作中引用并称之"
     "为「**中国古代的百科全书**」；2011 年入选联合国教科文组织《世界记忆名"
     "录》。与张仲景、华佗、孙思邈并称中国古代四大名医。",
     ["李时珍是哪个朝代的", "本草纲目写了多少年", "本草纲目记载多少种药",
      "达尔文怎么评价本草纲目", "世界记忆名录", "四大名医"],
     ["问中医诊疗方法", "问《伤寒杂病论》"],
     "atomic", "",
     "李时珍(1518-1593 明·蕲州)：27 年走遍南北三易其稿著《本草纲目》——190 万字 52 卷载药 1892 种附方 11096，首创矿物→植物→动物分类体系；译成多国文字，达尔文称「中国古代百科全书」；2011 入选世界记忆名录；四大名医之一。"),
    ("kp_card_teabrew",
     "泡茶的水温与冲泡",
     "生活常识知识点内容（人话接口）", "生活常识",
     "不同茶用不同水温（核心=**嫩芽低温、老叶沸水**）：①**绿茶**（龙井/碧螺"
     "春）——**75-85°C**（水烧开后晾 2-3 分钟）：嫩芽经不起沸水，烫熟会发黄"
     "发苦、维生素C损失；玻璃杯冲泡还可赏茶舞；②**红茶**——**90-95°C**；③"
     "**乌龙茶/黑茶（普洱）**——**95-100°C 沸水**：半发酵/后发酵茶需高温激发"
     "香气并紧压解块（紫砂壶/盖碗适合，可淋壶保温）；④**白茶**：新白茶 85-"
     "90°C、老白茶可煮饮。通用技巧：第一泡快速倒掉（**醒茶/洗茶**，尤其普洱）；"
     "绿茶不加盖（闷黄苦涩），乌龙普洱宜加盖闷香。健康提示：**浓茶伤胃+妨碍铁"
     "吸收**（饭后别立刻浓茶）、睡前少喝（咖啡因）、**隔夜茶不宜**（滋味劣变"
     "易滋生微生物）；「茶垢不洗更养壶」是误区——茶垢含多酚氧化物沉积应定期"
     "清洗。",
     ["泡绿茶用多少度的水", "红茶乌龙茶水温", "什么是洗茶",
      "绿茶为什么不能用沸水", "浓茶有什么坏处", "茶垢要不要洗"],
     ["问六大茶类分类（用茶文化卡）", "问茶道仪式流程"],
     "atomic", "",
     "泡茶水温=嫩芽低温老叶沸水：绿茶 75-85°C(烫熟发黄·玻璃杯)/红茶 90-95/乌龙普洱 95-100 紫砂盖碗；第一泡快速醒茶；绿茶不加盖乌龙宜闷香；浓茶伤胃碍铁吸收、隔夜茶不宜、茶垢应定期清洗（养壶≠留垢）。"),
]

QUESTIONS = [
    ("QB-733", "李时珍是哪个朝代的医药学家？《本草纲目》前后编撰了多少年？", "历史学", "技术直答",
     ["明朝", "明代", "27", "二十七", "蕲州"], "通识拓展159"),
    ("QB-734", "泡绿茶应该用多少度的水？为什么绿茶不能用刚烧开的沸水冲泡？", "生活常识", "技术直答",
     ["75", "80", "85", "烫熟", "发黄", "嫩芽"], "通识拓展159"),
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
                               "level:L2", "status:verified", "batch:通识拓展159"],
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
    bank["version"] = "v4.32"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
