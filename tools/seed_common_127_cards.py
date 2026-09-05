# -*- coding: utf-8 -*-
"""seed_common_127_cards.py · 通识拓展批次127知识卡+题库（幂等）

127：物理学-机械效率/化学-海水制镁/地理学-海洋污染/生活常识-网络暴力
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_meff",
     "机械效率",
     "基础科学知识点内容（人话接口）", "物理学",
     "机械效率（η）=有用功÷总功×100%——反映机械对能量利用的有效程度。为什么小"
     "于 100%：使用任何机械都不可避免做**额外功**（克服摩擦、提升机械本身重"
     "量）——有用功+额外功=总功。提高机械效率的方法：①减小摩擦（加润滑油）；②"
     "减小机械自重（轻量化设计）；③增加有用功占比（同一滑轮组提更重的物体——有"
     "用功占比增大）。实例：滑轮组提水的η=60-80%、起重机η=40-50%、现代火力发电"
     "η≈40%。与功率的区别：效率衡量「浪费多少」，功率衡量「快慢」——两者无直"
     "接关系（高效率≠大功率）。",
     ["什么是机械效率", "机械效率为什么小于100%", "如何提高机械效率",
      "机械效率和功率的区别", "滑轮组的机械效率", "额外功是什么"],
     ["问滑轮组效率计算", "问斜面效率实验"],
     "atomic", "",
     "机械效率 η=有用功/总功×100%：<100% 因额外功(摩擦+自重)不可避免；提高=减摩擦/轻量化/提更重物；与功率无直接关系(效率管浪费·功率管快慢)。"),
    ("kp_card_seamg",
     "海水制镁：从海水到金属镁",
     "基础科学知识点内容（人话接口）", "化学",
     "海水制镁的化学流程：①海水+石灰乳（Ca(OH)₂）→氢氧化镁沉淀 [MgCl₂+Ca(OH)₂"
     "→Mg(OH)₂↓+CaCl₂]；②氢氧化镁+盐酸→氯化镁 [Mg(OH)₂+2HCl→MgCl₂+2H₂O]；"
     "③氯化镁电解→金属镁+氯气 [MgCl₂→(通电) Mg+Cl₂↑]。镁是最轻的常用结构金"
     "属（密度 1.74g/cm³，约为铝的 2/3）——用于航空航天（减轻重量=省燃料）、汽"
     "车轻量化、笔记本电脑外壳。海水是镁的「无尽矿藏」：1 立方千米海水中含镁约"
     " 130 万吨。化学原理核心：沉淀→酸溶→电解，每一步都是典型的化学反应应用。",
     ["海水制镁的流程", "海水怎么提炼镁", "镁有什么用途", "海水中含量最多的金属离子",
      "电解氯化镁生成什么", "为什么用镁做飞机材料"],
     ["问海水提溴", "问镁合金应用"],
     "atomic", "",
     "海水制镁三步=石灰乳沉淀 Mg(OH)₂→盐酸溶解成 MgCl₂→电解得 Mg：镁是最轻结构金属(1.74g/cm³)用于航空航天；1km³ 海水含镁 130 万吨。"),
    ("kp_card_oceanpoll",
     "海洋污染",
     "人文通识知识点内容（人话接口）", "地理学",
     "海洋污染的主要来源：①**陆源排污**（约80%来自陆地）——工业废水/生活污水/"
     "农业化肥农药径流（近海富营养化→赤潮/绿潮）；②**石油泄漏**——油轮事故/海"
     "上钻井平台泄漏（康菲渤海漏油/深海地平线）——油膜隔绝氧气、毒死生物；③**塑"
     "料垃圾**——每年 800 万吨塑料入海（太平洋垃圾带面积超法国），微塑料进入食"
     "物链（人类每周摄入约 5 克塑料=一张信用卡）；④**过度捕捞**——渔业资源枯"
     "竭。治理：陆源截污、国际公约（MARPOL 防止船舶污染公约）、限塑令、海洋保护"
     "区。个人行动：减塑（自带购物袋/水杯）、不乱丢垃圾、参与净滩。",
     ["海洋污染的主要来源", "什么是赤潮", "太平洋垃圾带", "微塑料的危害",
      "怎么保护海洋环境", "石油泄漏对海洋的影响"],
     ["问微塑料人体健康", "问海洋保护公约"],
     "atomic", "",
     "海洋污染来源=陆源排污80%(富营养化赤潮)+石油泄漏(油膜缺氧)+塑料(年800万吨·微塑料入食物链)；治理=截污+MARPOL公约+限塑+个人减塑。"),
    ("kp_card_cyberbully",
     "网络暴力：无形的伤害",
     "生活常识知识点内容（人话接口）", "生活常识",
     "网络暴力：在网络上对他人进行言语攻击、人肉搜索、造谣诽谤、恶意P图等行为"
     "——「键盘侠」的伤害可以压垮一个人（多起网暴致抑郁自杀案例）。特点：①匿名"
     "性——施暴者隐藏身份肆无忌惮；②群体性——「法不责众」心理让人跟风攻击；③"
     "传播快——一次转发可能让谣言覆盖百万人。法律应对：《民法典》名誉权保护、"
     "《刑法》诽谤罪（情节严重可判刑）、2023 年《关于依法惩治网络暴力违法犯罪的"
     "指导意见》——网暴入罪明确化。个人防护：不参与骂战、不转发未经证实信息、"
     "遭遇网暴保留证据+报警+平台投诉。平台责任：实名制、一键防护、限流禁言。做"
     "理性网民：让子弹飞一会儿（不急于站队）、网暴受害者需要支持而非二次伤害。",
     ["什么是网络暴力", "网络暴力的危害", "遭遇网络暴力怎么办",
      "网暴会判刑吗", "人肉搜索违法吗", "如何做理性网民"],
     ["问网暴立法进展", "问平台算法责任"],
     "atomic", "",
     "网暴=言语攻击+人肉搜索+造谣P图：匿名+群体+传播快可压垮人(多起自杀案)；法律=民法典名誉权+刑法诽谤罪+2023指导意见；防护=留证据报警投诉；做理性网民。"),
]

QUESTIONS = [
    ("QB-643", "什么是机械效率", "物理学", "技术直答",
     ["有用功", "总功"], "通识拓展127"),
    ("QB-644", "海水制镁的流程", "化学", "技术直答",
     ["氢氧化镁", "电解"], "通识拓展127"),
    ("QB-645", "海洋污染的主要来源", "地理学", "技术直答",
     ["陆源排污", "石油泄漏", "塑料"], "通识拓展127"),
    ("QB-646", "什么是网络暴力", "生活常识", "技术直答",
     ["言语攻击", "人肉搜索"], "通识拓展127"),
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
                               "level:L2", "status:verified", "batch:通识拓展127"],
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
    bank["version"] = "v4.1"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
