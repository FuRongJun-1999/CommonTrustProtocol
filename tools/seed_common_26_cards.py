# -*- coding: utf-8 -*-
"""seed_common_26_cards.py · 通识拓展批次26知识卡+题库（幂等·既有域深化）

26：天文学-太阳成分/地理学-中国地势/化学-物理与化学变化/生物学-皮肤（深化既有域）
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_suncomposition",
     "太阳的成分与能量来源",
     "基础科学知识点内容（人话接口）", "天文学",
     "太阳主要由氢和氦组成：按质量约氢 74%、氦 24%，其余为少量重元素。太阳的"
     "能量来自核心的核聚变——四个氢原子核聚变成一个氦原子核，亏损的质量按爱因"
     "斯坦质能方程 E=mc² 释放为巨大能量；太阳每秒把数百万吨质量转化为能量，已"
     "稳定燃烧约 46 亿年，还能再燃烧约 50 亿年——「燃烧」是误称：太阳靠核聚变"
     "而非氧化燃烧，不需要氧气。太阳系质量的 99.86% 都集中在太阳。",
     ["太阳主要由什么元素组成", "太阳的能量从哪来", "太阳燃烧需要氧气吗",
      "什么是核聚变", "太阳还能燃烧多少年", "太阳系质量最大的天体"],
     ["问太阳黑子耀斑活动周期", "问恒星演化全流程"],
     "atomic", "",
     "太阳=氢74%+氦24%；能量=核心氢聚变氦(E=mc²)非氧化燃烧不需氧；已46亿年还能约50亿年；占太阳系质量99.86%。"),
    ("kp_card_chinaterrain",
     "中国地势三级阶梯",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国地势总特点：西高东低，呈三级阶梯状分布——第一阶梯：青藏高原（平均海"
     "拔 4000 米以上，「世界屋脊」）；第二阶梯：内蒙古高原/黄土高原/云贵高原与"
     "塔里木盆地/准噶尔盆地/四川盆地（1000-2000 米）；第三阶梯：东北平原/华北"
     "平原/长江中下游平原与东南丘陵（500 米以下）。阶梯交界处落差大、水流急，"
     "水能资源丰富（三峡工程位于二三阶梯交界）。西高东低还使大江大河大多自西"
     "向东流（长江/黄河），便于东西交通；地势对气候也有影响——东部季风区降水"
     "丰富。",
     ["中国地势有什么特点", "三级阶梯分别是什么", "世界屋脊指哪里",
      "长江黄河为什么自西向东流", "阶梯交界处水能为什么丰富", "三峡大坝位于哪两级阶梯交界"],
     ["问各省地形", "问四大高原细节对比"],
     "atomic", "",
     "中国地势=西高东低三级阶梯：青藏(4000m+)→高原盆地(1000-2000m)→平原丘陵(<500m)；交界处水能富/大河东流。"),
    ("kp_card_physchemchange",
     "物理变化与化学变化的区别",
     "基础科学知识点内容（人话接口）", "化学",
     "有无新物质生成是两者的根本区别：物理变化没有新物质生成——只是形态状态改"
     "变（冰融化成水、水蒸发、玻璃打碎、蜡烛受热熔化、纸张撕碎、酒精挥发）；化"
     "学变化（化学反应）有新物质生成（蜡烛燃烧生成二氧化碳和水、铁生锈、食物腐"
     "烂、木炭燃烧、粮食酿酒）。化学变化常伴随发光/放热/变色/生成气体或沉淀等现"
     "象，但这些现象只是辅助判断——灯泡通电发光发热却是物理变化。化学变化中一"
     "定同时发生物理变化（如蜡烛燃烧时蜡先熔化），反之不成立。",
     ["蜡烛燃烧是什么变化", "物理变化和化学变化怎么区分", "冰融化成水是什么变化",
      "铁生锈是什么变化", "灯泡发光发热是化学变化吗", "粮食酿酒是什么变化"],
     ["问质量守恒定律计算", "问化学反应四大类型"],
     "atomic", "",
     "根本区别=有无新物质：物理=状态形态(融化/挥发/碎裂)；化学=生成新物质(燃烧/生锈/腐烂)；发光放热≠化学(灯泡)。"),
    ("kp_card_skin",
     "皮肤：人体最大的器官",
     "基础科学知识点内容（人话接口）", "生物学",
     "皮肤是人体面积最大、重量最大的器官——成人皮肤总面积约 2 平方米、重量约"
     "占体重 16%。皮肤分三层：表皮（屏障+黑色素细胞防紫外线）、真皮（胶原弹力"
     "纤维+血管神经+汗腺毛囊）、皮下组织（脂肪保温缓冲）。功能：屏障保护（阻挡"
     "病菌与机械损伤）、感觉（触觉痛觉温觉感受器）、调节体温（出汗散热/血管收"
     "缩保温）、合成维生素 D（晒太阳帮助钙吸收）。「人体最大的器官是皮肤」是常"
     "考题——最大的内脏是肝脏。",
     ["人体最大的器官是什么", "皮肤分为哪三层", "皮肤有什么功能",
      "为什么晒太阳能补钙", "出汗是怎么散热", "最大的内脏器官是什么"],
     ["问烧伤分度处理", "问皮肤切口缝合等级"],
     "atomic", "",
     "皮肤=人体最大器官(约2m²·占体重16%)；三层=表皮/真皮/皮下；功能=屏障+感觉+调温+合成VD；最大内脏=肝脏。"),
]

QUESTIONS = [
    ("QB-237", "太阳主要由什么元素组成", "天文学", "技术直答",
     ["氢", "氦"], "通识拓展26"),
    ("QB-238", "中国地势有什么特点", "地理学", "技术直答",
     ["西高东低", "三级阶梯"], "通识拓展26"),
    ("QB-239", "蜡烛燃烧是什么变化", "化学", "技术直答",
     ["化学变化", "新物质"], "通识拓展26"),
    ("QB-240", "人体最大的器官是什么", "生物学", "技术直答",
     ["皮肤"], "通识拓展26"),
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
                               "level:L2", "status:verified", "batch:通识拓展26"],
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
    bank["version"] = "v1.18"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
