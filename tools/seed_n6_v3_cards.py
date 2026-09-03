# -*- coding: utf-8 -*-
"""seed_n6_v3_cards.py · 白箱知识域拓展第二批知识卡（幂等）

夜批N6（全天制首批）：人体生理/恒星演化/气候带/化学键 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_bloodcirc",
     "人体血液循环路径",
     "生活常识知识点内容（人话接口）", "人体生理",
     "人体血液循环分体循环与肺循环：体循环=左心室→主动脉→全身毛细血管"
     "（供氧交换）→上下腔静脉→右心房；肺循环=右心室→肺动脉→肺部毛细血管"
     "（吸氧排碳）→肺静脉→左心房。关键点：肺动脉里流的是静脉血（缺氧血），"
     "肺静脉里流的是动脉血（富氧血）——动脉/静脉以出发心脏的方向命名，不以血色命名。",
     ["人体血液循环路径", "血液循环怎么走", "体循环和肺循环", "肺动脉里流什么血",
      "心脏怎么供血", "问血液循环"],
     ["问消化系统", "问神经系统"],
     "atomic", "",
     "体循环=左心室→全身→右心房；肺循环=右心室→肺→左心房；肺动脉流静脉血、肺静脉流动脉血。"),
    ("kp_card_stellarevo",
     "恒星的生命周期",
     "基础科学知识点内容（人话接口）", "天文学",
     "恒星的生命周期由质量决定：星云引力坍缩→主序星（氢核聚变发光，太阳在此阶段"
     "约 100 亿年）→燃料耗尽后分岔——小质量恒星（如太阳）膨胀为红巨星→外层抛离"
     "成行星状星云→核心留为白矮星；大质量恒星（>8 倍太阳质量）超新星爆发→核心"
     "坍缩为中子星或黑洞。质量越大寿命越短（大恒星烧燃料更快）。",
     ["恒星的生命周期", "恒星怎么演化", "太阳最后会变成什么", "什么是白矮星",
      "什么是超新星", "恒星的一生", "黑洞是怎么形成的"],
     ["问系外行星", "问银河系结构"],
     "atomic", "",
     "恒星一生=星云→主序星→红巨星→（小质量）白矮星 /（大质量）超新星→中子星或黑洞；质量越大寿命越短。"),
    ("kp_card_climatezone",
     "世界气候带的分布",
     "基础科学知识点内容（人话接口）", "气候学",
     "世界气候带按纬度划分：热带（南北回归线之间，终年炎热）、温带（回归线到"
     "极圈，四季分明）、寒带（极圈内，终年严寒）。成因是太阳辐射随纬度变化——"
     "低纬太阳直射获热多，高纬斜射获热少。海洋与地形进一步细分气候（沿海温和、"
     "内陆干燥、高山垂直分带）。",
     ["世界气候带的分布", "什么是气候带", "热带温带寒带", "气候带怎么划分",
      "为什么低纬度热", "问气候类型"],
     ["问季风成因", "问厄尔尼诺"],
     "atomic", "",
     "气候带按纬度=热带（炎热）/温带（四季）/寒带（严寒），成因=太阳辐射随纬度递减。"),
    ("kp_card_chembond",
     "化学键的三种基本类型",
     "基础科学知识点内容（人话接口）", "化学键",
     "化学键的三种基本类型：离子键（原子得失电子形成阴阳离子，靠静电引力结合，"
     "如 NaCl）；共价键（原子间共用电子对，如 H₂O、O₂）；金属键（金属原子失电"
     "子成自由电子与金属阳离子共用，自由电子使金属导电导热有延展性）。判断：活"
     "泼金属+活泼非金属→离子键；非金属+非金属→共价键。",
     ["化学键有哪几种", "什么是离子键", "什么是共价键", "化学键的类型",
      "金属为什么导电", "离子键和共价键的区别"],
     ["问有机化学键", "问晶体结构"],
     "atomic", "",
     "化学键三类=离子键（得失电子静电引力）/共价键（共用电子对）/金属键（自由电子）；金属导电靠自由电子。"),
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
                "name": f"{name}（{dgroup}·基础科学知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——基础科学高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:夜间v0.3第二批"],
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
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
