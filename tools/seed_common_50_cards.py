# -*- coding: utf-8 -*-
"""seed_common_50_cards.py · 通识拓展批次50知识卡+题库（幂等）

50：物理学-家庭电路电压/化学-水的组成/生物学-种子的结构/历史-戊戌变法
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_220v",
     "家庭电路与安全电压",
     "基础科学知识点内容（人话接口）", "物理学",
     "我国家庭电路的电压是 220V（交流电，频率 50Hz）——火线与零线之间的电压；"
     "对人体的安全电压是不高于 36V（潮湿环境更低至 12V）。电流对人体的伤害：通"
     "过心脏的电流超过约 30mA 即可致命（电压越高越危险，100mA 以上短时致命）。"
     "家庭电路组成：进户线（火线 L/零线 N/地线 PE 三线）→电能表→总开关→保险装"
     "置→插座与用电器。用电原则：不接触低压带电体、不靠近高压带电体；开关必须"
     "接在火线上（断开后电器不带电）；大功率电器用三孔插座（地线接地防外壳带"
     "电）；测电笔辨火线零线（氖管发光=火线）。触电急救第一步：先断电源（或用干"
     "木棍挑开电线），绝不能直接用手拉。",
     ["我国家庭电路的电压是多少", "人体的安全电压是多少", "开关为什么要接在火线上",
      "三孔插座的第三个孔是什么", "触电了第一步做什么", "测电笔怎么用"],
     ["问漏电保护器原理", "问高压电弧触电"],
     "atomic", "",
     "家庭电路 220V/50Hz；安全电压≤36V(潮湿 12V)；30mA 过心脏致命；三线=火L/零N/地PE；开关接火线；触电急救=先断电不可手拉。"),
    ("kp_card_h2o_comp",
     "水的组成：电解水实验",
     "基础科学知识点内容（人话接口）", "化学",
     "水是由氢元素和氧元素组成的化合物（H₂O）——电解水实验是证据：通电后两极"
     "产生气体，正极氧气、负极氢气，体积比 V(氢):V(氧)=2:1（口诀「负氢正氧、氢"
     "二氧一」）；氢气能燃烧、氧气使带火星木条复燃。化学变化的本质：水分子分解成"
     "氢原子和氧原子，原子重新组合成氢分子和氧分子——原子是化学变化中的最小粒"
     "子。每个水分子由 2 个氢原子和 1 个氧原子构成。水的一些数据：4℃ 时密度最大"
     "（反常膨胀）、比热容大（调节气温/做冷却剂）、纯水几乎不导电（电解时要加少"
     "量氢氧化钠或硫酸钠增强导电性）。",
     ["水是由什么元素组成的", "电解水正极负极各产生什么", "氢气和氧气的体积比",
      "水分子由什么构成", "为什么电解水要加氢氧化钠", "原子和分子的区别"],
     ["问质量守恒的微观解释", "问水的净化对比电解"],
     "atomic", "",
     "水=氢+氧化合物(H₂O)；电解水：负氢正氧·体积比 2:1(负氢正氧氢二氧一)；微观=水分子→原子重组；原子=化学变化最小粒子；4℃ 密度最大。"),
    ("kp_card_seedstr",
     "种子的结构",
     "基础科学知识点内容（人话接口）", "生物学",
     "种子的主要结构是**胚**——新植株的幼体，由胚芽（发育成茎和叶）、胚轴（连接"
     "茎根）、胚根（发育成根）、子叶（储存或转运营养）四部分组成，外包种皮保护。"
     "双子叶植物（大豆/花生/菜豆）：两片子叶，营养储存在子叶里，无胚乳；单子叶植"
     "物（玉米/小麦/水稻）：一片子叶，营养储存在胚乳里。种子萌发条件：自身条件"
     "（胚完整有活力+度过休眠期）+外界条件（适宜的温度、充足的水分、充足的空气"
     "——缺一不可，光不是必要条件）。萌发过程：吸水膨胀→胚根先突破种皮发育成"
     "根→胚轴伸长→胚芽出土成茎叶。",
     ["种子的主要结构是什么", "胚包括哪几部分", "双子叶和单子叶的区别",
      "玉米和大豆的营养储存在哪里", "种子萌发需要什么条件", "种子萌发时先长什么"],
     ["问果实与种子关系复习", "问发芽率测定实验"],
     "atomic", "",
     "种子核心=胚(胚芽→茎叶/胚轴/胚根→根/子叶)；双子叶=两片子叶储养无胚乳(豆)；单子叶=一片子叶+胚乳储养(玉米麦)；萌发=活胚+温/水/气(光非必需)·胚根先出。"),
    ("kp_card_wuxu",
     "戊戌变法（百日维新）",
     "人文通识知识点内容（人话接口）", "历史",
     "戊戌变法（1898 年，农历戊戌年）：甲午战败（《马关条约》割地赔款）后民族危"
     "机加深，康有为、梁启超等维新派上书光绪皇帝（公车上书），主张学习西方、实"
     "行君主立宪、发展工商业、改革科举兴办新式学堂（京师大学堂=北京大学前身）。"
     "光绪帝 1898 年 6 月 11 日颁布《定国是诏》开始变法——但触怒以慈禧太后为首"
     "的顽固派，仅 103 天即告失败（史称「百日维新」）：慈禧发动戊戌政变囚禁光"
     "绪，谭嗣同、康广仁等「戊戌六君子」被杀（谭嗣同「我自横刀向天笑，去留肝胆"
     "两昆仑」慷慨赴死）。意义：虽败犹为近代思想启蒙——维新派宣传的进化论、天"
     "赋人权观念解放了思想，为辛亥革命铺路。",
     ["戊戌变法的领导人是谁", "百日维新为什么只持续了103天", "公车上书",
      "京师大学堂是哪所大学的前身", "戊戌六君子", "戊戌变法的意义"],
     ["问洋务运动对比", "问辛亥革命承接"],
     "atomic", "",
     "戊戌变法=1898 康有为梁启超辅光绪帝：君主立宪/兴学堂(京师大学堂→北大)；慈禧政变仅 103 天·六君子(谭嗣同)喋血；败而启蒙·为辛亥铺路。"),
]

QUESTIONS = [
    ("QB-333", "我国家庭电路的电压是多少", "物理学", "技术直答",
     ["220V", "220伏"], "通识拓展50"),
    ("QB-334", "水是由什么元素组成的", "化学", "技术直答",
     ["氢", "氧"], "通识拓展50"),
    ("QB-335", "种子的主要结构是什么", "生物学", "技术直答",
     ["胚"], "通识拓展50"),
    ("QB-336", "戊戌变法的领导人是谁", "历史", "技术直答",
     ["康有为", "梁启超"], "通识拓展50"),
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
                               "level:L2", "status:verified", "batch:通识拓展50"],
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
    bank["version"] = "v1.42"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
