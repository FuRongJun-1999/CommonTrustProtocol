# -*- coding: utf-8 -*-
"""seed_common_42_cards.py · 通识拓展批次42知识卡+题库（幂等）

42：化学-蜡烛燃烧去向/地理学-中国三大平原/生物学-人体骨骼/数学-角的分类
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_candlewhere",
     "蜡烛烧完去哪了：质量守恒",
     "基础科学知识点内容（人话接口）", "化学",
     "蜡烛燃烧变短，物质并没有消失——蜡烛（主要成分石蜡，碳氢化合物）与氧气反"
     "应，生成二氧化碳和水蒸气散逸到空气中。用质量守恒定律验证：密闭容器里称量，"
     "反应前后总质量完全相等；开放环境中「变少」只是生成物跑掉了。定量关系：约 "
     "44 克 CO₂ + 18 克 H₂O 生成对应的石蜡消耗。这正是「物质不灭」的化学证明，"
     "也是「蜡烛燃烧是化学变化」的核心证据（与 physchemchange 卡呼应：燃烧生成新"
     "物质）。铁器生锈变重同理——结合了空气中的氧。",
     ["蜡烛燃烧后变少了物质去哪了", "什么是质量守恒定律", "蜡烛燃烧的生成物",
      "怎么证明蜡烛燃烧生成二氧化碳和水", "铁生锈后质量为什么变重", "物质会消失吗"],
     ["问化学方程式配平", "问密闭容器实验设计"],
     "atomic", "",
     "蜡烛变短≠物质消失：石蜡+O₂→CO₂+水蒸气散逸；密闭容器称量前后相等=质量守恒；铁生锈变重同理（结合了氧）。"),
    ("kp_card_threeplains",
     "中国三大平原",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国三大平原（都在地势第三阶梯，自北向南）：①东北平原——面积最大（约 35 "
     "万平方公里），黑土肥沃（「黑土地」，商品粮基地，北大荒变北大仓）；②华北平"
     "原——又称黄淮海平原，由黄河/淮河/海河冲积而成，人口密集，小麦玉米主产"
     "区；③长江中下游平原——河湖密布（「鱼米之乡」），水田农业。平原的形成：主"
     "要是河流携带泥沙长期堆积（冲积平原）。三大平原是中国最重要的农耕区与城市群"
     "聚集地（东北粮仓/京津冀/长三角）。丘陵与平原区别：平原海拔一般低于 200 米"
     "且地势平坦。",
     ["中国三大平原是什么", "东北平原的土壤特点", "华北平原是怎么形成的",
      "鱼米之乡指哪里", "北大荒变北大仓什么意思", "中国最大的平原"],
     ["问丘陵山地分布", "问黑土保护政策"],
     "atomic", "",
     "三大平原=东北(最大·黑土粮仓)+华北(黄淮海冲积·麦区)+长江中下游(鱼米之乡)；均为河流冲积成、第三阶梯；平原<200m 平坦。"),
    ("kp_card_bones206",
     "人体的骨骼",
     "基础科学知识点内容（人话接口）", "生物学",
     "成年人体共有 206 块骨（婴儿出生时 300 多块，发育中部分骨愈合所以变少）。"
     "骨骼的功能：支撑身体（支架）、保护内脏（颅骨护脑/肋骨护心肺）、运动杠杆"
     "（骨+关节+肌肉协同）、造血（红骨髓制造血细胞）、储存钙磷。脊柱从侧面看有"
     "四个生理弯曲（颈/胸/腰/骶曲）——缓冲震荡、直立行走的关键；「一脊柱二三十"
     "三块椎骨」中颈椎 7 块、胸椎 12 块、腰椎 5 块。关节是骨连接的形式之一（能活"
     "动），软骨减少会关节炎。补钙关键期在青少年；维生素 D 帮助钙吸收（晒太阳）。"
     "人体最强的骨是股骨（大腿骨）。",
     ["人体有多少块骨头", "骨骼有什么功能", "婴儿骨头比成人多吗",
      "脊柱有几个生理弯曲", "人体最长的骨是哪块", "为什么晒太阳对骨骼好"],
     ["问关节炎类型", "问骨折愈合过程"],
     "atomic", "",
     "成人 206 块骨(婴儿300+渐愈合)；功能=支撑/保护(颅护脑肋护心肺)/运动杠杆/红骨髓造血/储钙磷；脊柱四曲缓冲·颈椎7胸12腰5；最强=股骨。"),
    ("kp_card_angles",
     "角的分类与度数",
     "基础科学知识点内容（人话接口）", "数学",
     "角按度数分类（1°=把圆周 360 等分的一份对角）：锐角（大于 0° 小于 90°）、"
     "直角（等于 90°，如书本角/墙角）、钝角（大于 90° 小于 180°）、平角（等于 "
     "180°，一条直线）、周角（等于 360°，转一整圈）。换算关系：1 平角=2 直角、"
     "1 周角=4 直角。角的度量工具是量角器（对中心、对零线、读刻度）。相关概念："
     "角的两条边是射线；对顶角相等；三角形三个内角和 180°（与角分类卡呼应）——"
     "三个角都是锐角的三角形叫锐角三角形，有一个直角叫直角三角形。",
     ["锐角钝角直角怎么分", "什么是平角和周角", "一个周角等于几个直角",
      "量角器怎么用", "钝角的范围是多少度", "三角形按角怎么分类"],
     ["问余角补角计算", "问角的弧度制"],
     "atomic", "",
     "角分类：锐<90°=直=90°<钝<180°=平=180°=周=360°；1平角=2直角、1周角=4直角；量角器=对中心/对零线/读刻度；两边是射线。"),
]

QUESTIONS = [
    ("QB-301", "蜡烛燃烧后变少了物质去哪了", "化学", "技术直答",
     ["质量守恒", "二氧化碳", "水"], "通识拓展42"),
    ("QB-302", "中国三大平原是什么", "地理学", "技术直答",
     ["东北平原", "华北平原", "长江中下游平原"], "通识拓展42"),
    ("QB-303", "人体有多少块骨头", "生物学", "技术直答",
     ["206"], "通识拓展42"),
    ("QB-304", "锐角钝角直角怎么分", "数学", "技术直答",
     ["90度", "直角"], "通识拓展42"),
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
                               "level:L2", "status:verified", "batch:通识拓展42"],
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
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.34"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
