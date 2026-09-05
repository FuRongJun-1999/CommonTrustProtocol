# -*- coding: utf-8 -*-
"""seed_common_125_cards.py · 通识拓展批次125知识卡+题库（幂等）

125：物理学-常见家电功率/化学-纳米材料/生物学-外来物种入侵/地理学-中国人口迁移
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_apppower",
     "常见家电的功率",
     "基础科学知识点内容（人话接口）", "物理学",
     "常见家电功率参考（瓦 W）：①大功率——空调挂机 1000-1500W、电热水器"
     " 2000-3000W、电磁炉 2000W、电吹风 1000-2000W、微波炉 1000W；②中功率——"
     "电饭锅 700W、电水壶 1500W（短时）、洗衣机 500W、电视 100-200W；③小功率"
     "——冰箱 100-200W（间歇工作）、LED 灯 5-20W、手机充电器 10-30W、路由器 10W"
     "。节电要点：大功率电器错峰使用、冰箱避免频繁开门（每次开门压缩机重新启"
     "动）、LED 替代白炽灯（同亮度省电 80%+）。耗电估算公式：用电量（度）=功率"
     "（kW）×时间（h）——1.5kW 空调开 8 小时=12 度电。",
     ["常见家电的功率", "什么家电最耗电", "空调一小时几度电",
      "LED灯为什么省电", "怎么估算家电耗电量", "冰箱一天用几度电"],
     ["问空调变频原理", "问家庭节电技巧"],
     "atomic", "",
     "家电功率参考：空调 1-1.5kW/电磁炉 2kW/热水器 2-3kW（大）·冰箱 150W·LED 10W（小）；耗电=kW×h；LED 替白炽灯省 80%+；大功率错峰+冰箱少开门。"),
    ("kp_card_nanomaterial",
     "纳米材料",
     "基础科学知识点内容（人话接口）", "化学",
     "纳米材料：至少一维尺寸在 **1-100 纳米**（nm，1nm=10⁻⁹ 米，头发直径的十万"
     "分之一）的材料。纳米效应：尺寸小到纳米级时，**表面效应**（表面原子比例急"
     "剧增大——活性增强）与**小尺寸效应**（量子尺寸效应）使材料呈现全新性质——"
     "例：纳米银（强抗菌——用于袜子/口罩/医用敷料）、纳米二氧化钛（自清洁玻璃"
     "——光催化分解污渍）、碳纳米管（强度是钢的 100 倍、导电超铜）。应用：纳"
     "米药物（靶向递药）、防水涂层（荷叶效应）、防晒霜（纳米二氧化钛散射紫外"
     "线）。安全性：纳米颗粒可入肺入血——安全性评估仍在研究（「纳米毒理学」）。",
     ["纳米材料是什么", "纳米材料有什么特性", "纳米银有什么用",
      "纳米材料的尺寸范围", "纳米二氧化钛的作用", "纳米材料安全吗"],
     ["问石墨烯与纳米", "问纳米医药进展"],
     "atomic", "",
     "纳米材料=1-100nm：表面效应+量子效应→新性质；例=纳米银抗菌/纳米TiO₂自清洁/碳纳米管强 100 倍钢；应用=靶向药物/防水涂层/防晒；安全性研究进行中。"),
    ("kp_card_invasivesp",
     "外来物种入侵",
     "基础科学知识点内容（人话接口）", "生物学",
     "外来物种入侵：物种被人为或自然引入其**原生地之外**的区域，因缺乏天敌而"
     "疯狂繁殖，挤占本土物种生态位、破坏生态平衡。中国著名入侵物种：①**水葫"
     "芦**（凤眼蓝）——堵塞河道、遮蔽阳光致水体缺氧（治理：打捞+资源化利用）；"
     "②**福寿螺**——啃食水稻、传播寄生虫（广州管圆线虫）；③**红火蚁**——叮咬"
     "人畜（过敏休克）、破坏电器设施；④**加拿大一枝黄花**——「生态杀手」，化感"
     "作用抑制周围植物。入侵途径：有意引入（观赏/养殖后逃逸）+无意带入（货物"
     "夹带/压舱水）。防控：《生物安全法》+海关检疫+全民报告（发现上报农业部门）"
     "——不随意放生宠物（巴西龟/鳄雀鳝）。",
     ["外来物种入侵的危害", "水葫芦的危害", "福寿螺的危害",
      "红火蚁是什么", "巴西龟为什么不能放生", "鳄雀鳝是什么"],
     ["问生物入侵经典案例", "问海关检疫流程"],
     "atomic", "",
     "入侵物种=引入新区域缺乏天敌疯狂繁殖：水葫芦堵河道/福寿螺啃稻传播寄生"
     "虫/红火蚁叮咬破坏电器/加拿大一枝黄花化感排挤；防控=海关检疫+不随意放生。"),
    ("kp_card_popmigrate",
     "中国的人口迁移",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国人口迁移主趋势：**农村→城市、内地→沿海、经济欠发达→发达地区**。改革"
     "开放后「民工潮」：数亿农村劳动力涌入珠三角/长三角/京津冀——原因：城乡收入"
     "差距+沿海制造业岗位需求。近年新趋势：①产业转移带动「回流」（内地城市承接"
     "沿海产业——就近就业）；②新型城镇化：户籍改革放宽落户（除超大城市）；③"
     "人口向都市圈城市群集聚（长三角/珠三角/成渝）。影响：迁出地——留守儿童/老"
     "人、土地撂荒；迁入地——劳动力供给/公共服务压力/房价。户籍制度：城乡二元结"
     "构的历史产物，改革方向=居住证制度+公共服务均等化。",
     ["中国人口迁移的主要方向", "民工潮是什么", "为什么人口向沿海迁移",
      "人口回流的原因", "留守儿童问题", "户籍制度改革方向"],
     ["问城市群人口虹吸", "问县域经济"],
     "atomic", "",
     "迁移主线=乡村→城市·内地→沿海·欠发达→发达（民工潮·城乡收入差+岗位需求）；新趋势=产业转移回流+都市圈集聚；影响=留守群体 vs 公共服务压力；户籍改革=居住证+均等化。"),
]

QUESTIONS = [
    ("QB-635", "常见家电的功率", "物理学", "技术直答",
     ["空调", "电磁炉", "LED"], "通识拓展125"),
    ("QB-636", "纳米材料是什么", "化学", "技术直答",
     ["1-100纳米", "表面效应"], "通识拓展125"),
    ("QB-637", "外来物种入侵的危害", "生物学", "技术直答",
     ["水葫芦", "福寿螺", "红火蚁"], "通识拓展125"),
    ("QB-638", "中国人口迁移的主要方向", "地理学", "技术直答",
     ["农村到城市", "内地到沿海"], "通识拓展125"),
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
                               "level:L2", "status:verified", "batch:通识拓展125"],
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
    bank["version"] = "v3.9"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
