# -*- coding: utf-8 -*-
"""seed_common_82_cards.py · 通识拓展批次82知识卡+题库（幂等）

82：物理学-电路的组成/化学-二氧化碳的用途/生物学-动植物细胞的区别/地理学-交通运输方式选择
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_circuit4",
     "电路的组成",
     "基础科学知识点内容（人话接口）", "物理学",
     "一个完整的电路由四部分组成：①**电源**（提供电能——干电池/蓄电池/发电机，"
     "把其他形式能转化为电能）；②**用电器**（消耗电能工作——灯泡/电动机，把电"
     "能转化为其他形式能）；③**开关**（控制电路通断）；④**导线**（连接输送电"
     "能）。状态：通路（处处连通有电流）、开路/断路（某处断开无电流）、**短路**"
     "（不经过用电器直接连通电源——电流过大烧坏电源/导线，绝对禁止！）。电路图"
     "用统一符号画（国家规定标准符号）。串联：首尾相连一条路径（一处断处处断，"
     "开关控制整个电路）；并联：并列多条路径（互不影响，干路开关控全部、支路开"
     "关控本支路）——家庭电路是并联（各电器独立工作）。",
     ["一个完整的电路由哪几部分组成", "什么是短路", "串联和并联的区别",
      "家庭电路是串联还是并联", "电源的作用是什么", "什么是通路开路短路"],
     ["问串并联识别技巧", "问电路故障判断"],
     "atomic", "",
     "电路四件=电源(供能)+用电器(耗能)+开关(控断通)+导线(输送)；短路=不经用电器直连电源(危险禁)；串联一条路互影响·并联多路径互独立——家庭=并联。"),
    ("kp_card_co2uses",
     "二氧化碳的用途",
     "基础科学知识点内容（人话接口）", "化学",
     "二氧化碳的性质决定用途：①不燃烧不支持燃烧+密度大于空气→**灭火**（CO₂ 灭"
     "火器——图书档案精密仪器适用，不留痕迹）；②固态干冰升华吸热→**人工降雨**"
     "（凝结核+降温）、舞台云雾、食品保鲜运输；③溶于水生成碳酸→**碳酸饮料**；"
     "④光合作用原料→**温室气肥**（提高大棚作物产量）；⑤化工原料——制纯碱/尿"
     "素/碳酸饮料；⑥液态 CO₂ 用于超临界萃取（咖啡因脱除）。人体产生 CO₂ 是正常"
     "代谢（呼吸出），不是「废气」意义上全是毒——密闭空间浓度过高才致窒息（缺氧"
     "为主）。CO₂ 与「温室气体」的双面性：太低植物减产、太高全球变暖——目标不是"
     "归零而是平衡。",
     ["二氧化碳有什么用途", "干冰有什么用", "为什么CO₂能灭火",
      "温室里施二氧化碳气肥", "二氧化碳有毒吗", "人工降雨的原理"],
     ["问碳捕集 CCUS", "问 CO₂ 超临界应用"],
     "atomic", "",
     "CO₂ 用途=灭火(不燃不助燃·密度大)+干冰(降雨/保鲜/舞台雾)+碳酸饮料+温室气肥+化工原料；呼出 CO₂=正常代谢非毒气；温室气体平衡≠归零。"),
    ("kp_card_cellcmp",
     "动植物细胞的区别",
     "基础科学知识点内容（人话接口）", "生物学",
     "动植物细胞共同结构：细胞膜（控制物质进出）、细胞质、细胞核（含遗传物质）、"
     "线粒体（呼吸作用供能）。**植物细胞特有的三件**：①细胞壁（支持保护，纤维素"
     "构成）；②液泡（内含细胞液——西瓜的甜味/酸味就在这里）；③叶绿体（光合作用"
     "场所）。动物细胞没有这三样。人体/动物细胞也没有细胞壁——所以青霉素杀菌"
     "（破坏细菌细胞壁）对人体细胞影响小（细菌也有细胞壁）。观察实验：洋葱表皮"
     "细胞（易取材看细胞壁液泡）与人的口腔上皮细胞（看细胞膜细胞核电细胞质）对"
     "比——碘液染色便于观察细胞核。",
     ["植物细胞和动物细胞的区别", "植物细胞特有的结构", "液泡里含有什么",
      "青霉素为什么能杀菌", "细胞膜的作用", "洋葱表皮实验看什么"],
     ["问细胞结构功能表", "问显微镜使用规范"],
     "atomic", "",
     "共有=细胞膜/细胞质/细胞核/线粒体；植物独有=细胞壁(纤维素支持)+液泡(细胞液·西瓜甜)+叶绿体(光合)；动物三无；青霉素破细菌细胞壁故对人温和。"),
    ("kp_card_transpick",
     "交通运输方式的选择",
     "人文通识知识点内容（人话接口）", "地理学",
     "现代五大运输方式的特点与选择：①铁路——运量大、速度较快、运费较低、受天"
     "气影响小（大宗中长距离：煤炭/粮食/整车）；②公路——机动灵活、实现「门到"
     "门」（短途、鲜活易腐、小批量）；③水运——运量最大、运费最低、但速度慢受"
     "自然限制（大宗笨重远距离不急的：矿石/粮食/集装箱）；④航空——最快、运量"
     "小运费高（贵重、急需、鲜活高档：急救药品/精密仪器/鲜花）；⑤管道——连续"
     "性强、安全损耗小（液体气体：石油/天然气）。选择口诀：「贵重急需选航空，大"
     "宗笨重水运省，短途零担公路便，大宗中长铁路廉」。中国：高铁里程世界第一，"
     "「八纵八横」高铁网；港口吞吐量世界前十占七席。",
     ["运货物怎么选择运输方式", "五大运输方式的特点", "鲜花开长途用什么运输",
      "水运的优点是什么", "中国高铁里程世界第几", "管道运输适合什么货物"],
     ["问多式联运", "问物流成本构成"],
     "atomic", "",
     "五运方式选择：贵重急需→航空；大宗笨重远距→水运(最廉)或铁路；短途灵活→公路(门到门)；液气连续→管道；口诀「贵急航空大宗水·短途公路中长铁」。"),
]

QUESTIONS = [
    ("QB-461", "一个完整的电路由哪几部分组成", "物理学", "技术直答",
     ["电源", "用电器", "开关", "导线"], "通识拓展82"),
    ("QB-462", "二氧化碳有什么用途", "化学", "技术直答",
     ["灭火", "干冰", "气肥"], "通识拓展82"),
    ("QB-463", "植物细胞和动物细胞的区别", "生物学", "技术直答",
     ["细胞壁", "液泡", "叶绿体"], "通识拓展82"),
    ("QB-464", "运货物怎么选择运输方式", "地理学", "技术直答",
     ["贵重航空", "大宗水运", "短途公路"], "通识拓展82"),
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
                               "level:L2", "status:verified", "batch:通识拓展82"],
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
    bank["version"] = "v1.74"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
