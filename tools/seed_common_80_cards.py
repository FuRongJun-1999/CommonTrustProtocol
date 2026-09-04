# -*- coding: utf-8 -*-
"""seed_common_80_cards.py · 通识拓展批次80知识卡+题库（幂等）

80：物理学-机械能守恒/化学-溶液配制/生物学-生物多样性/地理学-中国的自然资源
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_mechenergy",
     "机械能及其转化：过山车的秘密",
     "基础科学知识点内容（人话接口）", "物理学",
     "动能（运动具有的能，与质量和速度有关）+势能（重力势能与高度有关、弹性势"
     "能与形变有关）合称机械能。**动能和势能可以相互转化**：过山车冲上高处——动"
     "能→重力势能；俯冲而下——势能→动能（速度最大在最低点）；撑杆跳——动能→"
     "弹性势能→重力势能。若只有重力/弹力做功（无摩擦阻力），机械能总量保持不变"
     "（机械能守恒）——现实中有摩擦，机械能会逐渐转化为内能，所以过山车第一座"
     "山**最高**（后面越滚越低，靠中途驱动站补能）。滚摆/单摆/水电站（势能→动"
     "能→电能）都是转化实例。荡秋千不继续推会越荡越低——机械能被空气阻力消耗。",
     ["过山车为什么不用发动机也能冲上去", "什么是机械能守恒", "动能和势能怎么转化",
      "过山车第一座山为什么最高", "水电站的能量转化", "荡秋千为什么越荡越低"],
     ["问能量转化复习", "问机械能守恒计算题"],
     "atomic", "",
     "机械能=动能+势能；过山车=动能⇄势能循环·无摩擦守恒·现实有摩擦故第一山最高；实例=撑杆跳(动→弹→重)/水电站(势→动→电)；秋千越荡越低=阻力耗能。"),
    ("kp_card_solutionprep",
     "配制一定溶质质量分数的溶液",
     "基础科学知识点内容（人话接口）", "化学",
     "实验室配制 50g 质量分数 10% 的氯化钠溶液四步：①**计算**——溶质=50×10%=5g"
     "，水=45g（45mL）；②**称量**——托盘天平称 5g 氯化钠，量筒量取 45mL 水（量"
     "筒选一次能量取的最小规格，仰视读数偏小实际偏多、俯视反之）；③**溶解**——"
     "倒入烧杯用玻璃棒搅拌（加速溶解）；④**装瓶贴签**——贴上标签（名称+浓度）。"
     "误差分析：称量物放右盘（用了游码）→实际偏小浓度偏低；仰视量水→水多→浓度"
     "偏低；氯化钠不纯或洒落→偏低。仪器：托盘天平、量筒、烧杯、玻璃棒、药匙。浓"
     "溶液稀释：稀释前后**溶质质量不变**（C1V1=C2V2 思想）。",
     ["配制一定溶质质量分数溶液的步骤", "配制溶液需要哪些仪器", "量筒读数误差",
      "玻璃棒在溶解中的作用", "稀释溶液溶质质量怎么算", "配制的溶液浓度偏低原因"],
     ["问浓硫酸稀释安全", "问溶液计算综合"],
     "atomic", "",
     "配制四步=计算→称量(天平+量筒)→溶解(玻璃棒搅)→装瓶贴签；误差：物放右盘/仰视量水/药品不纯→偏低；玻璃棒=加速溶解；稀释前后溶质不变。"),
    ("kp_card_biodiv",
     "生物多样性三层次",
     "基础科学知识点内容（人话接口）", "生物学",
     "生物多样性包括三个层次：①**基因（遗传）多样性**——同种生物个体基因组成"
     "的差异（不同品种的水稻/狗的品种繁多）；②**物种多样性**——物种种类的丰富"
     "程度（中国是生物多样性大国：已知物种约 10 万+，鸟类/鱼类/高等植物种数世界"
     "前列）；③**生态系统多样性**——森林/草原/荒漠/湿地/海洋等生态系统类型的丰"
     "富。三者关系：基因多样性支撑物种多样性，多样的物种构成多样的生态系统。价值"
     "：直接价值（食用药用工业原料）、间接价值（生态功能——涵养水源/调节气候，"
     "远大于直接价值）、潜在价值（未知的基因资源）。威胁：栖息地破坏（首要因"
     "素）/过度捕猎/外来物种入侵/环境污染。保护措施：就地保护（建立自然保护区——"
     "最有效）、迁地保护（动物园/植物园/种子库——如中国西南野生生物种质资源"
     "库）、法律法规（野生动物保护法）。",
     ["生物多样性包括哪三个层次", "保护生物多样性最有效的措施",
      "什么是外来物种入侵", "种子库是干什么的", "生物多样性的价值",
      "威胁生物多样性的原因"],
     ["问自然保护区案例", "问入侵物种案例"],
     "atomic", "",
     "生物多样性三层次=基因(品种差异)/物种(种类丰富)/生态系统(类型多样)；保护最有效=就地保护(自然保护区)+迁地(种质库)；首要威胁=栖息地破坏；间接价值>直接。"),
    ("kp_card_natureres",
     "中国的自然资源",
     "人文通识知识点内容（人话接口）", "地理学",
     "自然资源=自然界中对人类有利用价值的物质与能量（土地/水/气候/生物/矿产/海"
     "洋资源）。分类：可再生（土地/水/气候/生物——短期能更新）与不可再生（矿产"
     "——亿万年级）。中国自然资源总特点：**总量丰富、人均不足**——耕地/河流径流"
     "量/矿产总量世界前列，但人均占有量多低于世界平均（人均耕地约为世界 40%）。"
     "土地利用：耕地/林地/草地/建设用地——「十分珍惜、合理利用土地和切实保护耕"
     "地」是基本国策（18 亿亩耕地红线）。水资源：总量大人均少+时空分布不均（南多"
     "北少、夏秋多冬春少）→跨流域调水（南水北调）与修建水库。矿产：煤北方、石油"
     "北方与沿海大陆架、有色金属南方（「南有色金属北煤油」）；稀土储量世界第"
     "一。",
     ["中国的自然资源特点", "自然资源分哪两类", "18亿亩耕地红线",
      "中国水资源分布特点", "稀土储量世界第一", "南水北调解决什么问题"],
     ["问土地基本国策", "问自然资源法体系"],
     "atomic", "",
     "自然资源=可再生(土地水气候生物)+不可再生(矿产)；中国=总量丰富人均不足(人均耕地≈世界 40%)；国策=保护耕地 18 亿亩红线；水=南多北少→南水北调+水库；稀土世界第一。"),
]

QUESTIONS = [
    ("QB-453", "过山车为什么不用发动机也能冲上去", "物理学", "技术直答",
     ["动能", "势能", "转化"], "通识拓展80"),
    ("QB-454", "配制一定溶质质量分数溶液的步骤", "化学", "技术直答",
     ["计算", "称量", "溶解"], "通识拓展80"),
    ("QB-455", "生物多样性包括哪三个层次", "生物学", "技术直答",
     ["基因", "物种", "生态系统"], "通识拓展80"),
    ("QB-456", "中国的自然资源特点", "地理学", "技术直答",
     ["总量丰富", "人均不足"], "通识拓展80"),
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
                               "level:L2", "status:verified", "batch:通识拓展80"],
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
    bank["version"] = "v1.72"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
