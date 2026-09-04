# -*- coding: utf-8 -*-
"""seed_n16_v3_cards.py · 知识域拓展批次知识卡（幂等）

16：声学-超声波与次声波/化学-溶液与溶解度/物理-压强/地理-地球内部圈层
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_ultrasonic",
     "超声波与次声波",
     "基础科学知识点内容（人话接口）", "声学",
     "超声波：频率高于 20000Hz 的声波，人耳听不到，方向性好穿透力强——应用="
     "B超（医学成像）、声呐（潜艇探测）、超声清洗（眼镜珠宝）、超声碎结石。次"
     "声波：频率低于 20Hz 的声波，人耳也听不到，传播距离极远——自然灾害（地震"
     "海啸火山喷发）常伴随次声波，可作预警；军事上用于监测核爆炸。",
     ["超声波和次声波", "超声波", "什么是次声波", "超声波的应用",
      "B超用的什么波", "次声波的用途"],
     ["问声音三要素", "问噪声控制"],
     "atomic", "",
     "超声波>20000Hz（B超/声呐/清洗）；次声波<20Hz（灾害预警/监测核爆）；人耳只听 20Hz-20000Hz。"),
    ("kp_card_solution",
     "溶液与溶解度",
     "基础科学知识点内容（人话接口）", "化学",
     "溶液：一种物质（溶质）溶解在另一种物质（溶剂）中形成的均匀稳定的混合物"
     "——如食盐溶于水形成食盐溶液。溶解度：在一定温度下某物质在 100g 溶剂中达"
     "到饱和状态时所能溶解的最大质量（g）。多数固体溶解度随温度升高而增大（如"
     "硝酸钾），少数变化不大（如氯化钠），极少数随温度升高反而减小（如氢氧化钙"
     "熟石灰）。气体溶解度随温度升高而减小、随压强增大而增大（打开汽水冒气泡）。",
     ["什么是溶液", "溶液与溶解度", "溶解度", "溶液的组成", "影响溶解度的因素",
      "为什么打开汽水会冒气泡"],
     ["问结晶方法", "问乳浊液"],
     "atomic", "",
     "溶液 = 溶质+溶剂均匀稳定混合物；溶解度=100g溶剂中饱和溶解量；固体多随温升增大/气体随温升减小。"),
    ("kp_card_pressure",
     "压强",
     "基础科学知识点内容（人话接口）", "物理学",
     "压强：物体单位面积上受到的压力，公式 p = F/S（压力除以受力面积），单位"
     "帕斯卡（Pa）。增大压强：增大压力或减小受力面积（刀刃磨锋利、图钉尖细）；"
     "减小压强：减小压力或增大受力面积（书包带做宽、坦克装履带、铁轨枕木）。液"
     "体内部压强随深度增加而增大，同一深度各方向压强相等——大坝上窄下宽因此。",
     ["什么是压强", "压强的公式", "增大压强的方法", "减小压强的方法",
      "压强的单位", "为什么书包带做宽"],
     ["问大气压强", "问液体压强"],
     "atomic", "",
     "压强 p = F/S（Pa）；增大=增大压力/减小面积（刀刃），减小=减力/增面积（履带宽带）。"),
    ("kp_card_earthlayers",
     "地球的内部圈层结构",
     "基础科学知识点内容（人话接口）", "地理学",
     "地球内部圈层（由外到内）：①地壳——最薄的固体岩石层（大陆约 35km、海洋"
     "约 6km），人类活动的场所；②地幔——最厚的一层（约 2900km 深度），上部软"
     "流层是岩浆发源地（板块运动的动力来源）；③地核——半径约 3400km，分外地"
     "核（液态铁镍）和内地核（固态铁镍）。科学家通过地震波（纵波与横波传播速"
     "度差异）来研究地球内部结构——像给地球做B超。",
     ["地球的内部圈层", "地球内部结构", "地壳地幔地核", "地球分几层",
      "科学家怎么研究地球内部", "地球最里面是什么"],
     ["问板块运动", "问地震波"],
     "atomic", "",
     "地球内三圈 = 地壳（薄）→地幔（厚，软流层=岩浆源）→地核（外液内固铁镍）；地震波探内。"),
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
                               "level:L2", "status:verified", "batch:通识拓展09"],
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
