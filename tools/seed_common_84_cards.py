# -*- coding: utf-8 -*-
"""seed_common_84_cards.py · 通识拓展批次84知识卡+题库（幂等）

84：物理学-超导材料/化学-元素的分类/生物学-细菌的结构/地理学-台风
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_supercond",
     "超导体：零电阻的奇迹",
     "基础科学知识点内容（人话接口）", "物理学",
     "超导体：温度降到某一临界温度以下时电阻变为**零**的材料——电流在其中流动"
     "不损耗能量（1911 年昂内斯发现水银在 4.2K 时电阻消失，获诺奖）。应用前景："
     "①零损耗输电（省下目前约 10% 的线损）；②强磁体——磁悬浮列车（超导磁体悬"
     "浮，沪杭磁悬浮设想）、核磁共振成像（MRI）、可控核聚变的约束磁体（EAST 全"
     "超导托卡马克）；③超导计算机（超高速低功耗）。现状挑战：传统超导体需极低温"
     "（液氦 -269℃ 级），维持成本高；高温超导体（液氮 -196℃ 级，1986 年突破，"
     "中国赵忠贤团队贡献大）已降低门槛，但室温常压超导体仍未实现——「室温超导」"
     "是材料学圣杯（近年多篇「突破」论文因造假/不可复现撤稿，如 2023 年美国"
     " Ranga Dias 事件，科研诚信警示）。",
     ["超导体有什么特性", "超导体能用来做什么", "什么是高温超导体",
      "室温超导实现了吗", "磁悬浮列车的原理", "赵忠贤的贡献"],
     ["问迈斯纳效应", "问超导输电经济账"],
     "atomic", "",
     "超导体=临界温度以下电阻为零(1911 昂内斯)：应用=零损耗输电/磁悬浮/MRI/聚变磁体；高温超导(液氮级·赵忠贤)降门槛；室温常压仍是圣杯——Dias 撤稿为诚信警示。"),
    ("kp_card_elem3type",
     "元素的三大分类",
     "基础科学知识点内容（人话接口）", "化学",
     "化学元素按性质分三类：①**金属元素**（约 80%，最多）——钠镁铝钾钙铁锌铜银"
     "金汞等：有金属光泽、能导电导热、有延展性（除汞常温为液态——「水银」）；名"
     "字多带「钅」旁（汞除外）。②**非金属元素**——氢氧氮碳硫磷氯等：无金属光"
     "泽、不导电（石墨例外）、名带「气」「石」「氵」旁（气态：氢氧氮氯；固态：碳"
     "硫磷碘；液态唯一：溴）。③**稀有气体元素**——氦氖氩氪氙氡（0 族，性质极不"
     "活泼）。记忆锚点：地壳前五=氧硅铝铁钙；人体前四=氧碳氢氮。元素中文名称由"
     "清末徐寿系统创译（造字如「锌」「镁」「氟」），朱元璋后代名字贡献了一批金"
     "属字（朱慎镭——「镭」字早于镭发现，趣闻）。",
     ["元素分为哪三类", "常温下唯一呈液态的非金属", "地壳中含量最多的金属元素",
      "金属和非金属怎么区分", "稀有气体包括哪些", "汉字元素名的来历"],
     ["问元素周期表分区", "问金属之最盘点"],
     "atomic", "",
     "元素三类=金属(80%·钅旁·汞为液)非金属(气石氵·溴唯一液态)稀有气体(HeNeArKrXeRn)；地壳前五氧硅铝铁钙·最多金属=铝；徐寿创译汉字元素名。"),
    ("kp_card_bacteriastr",
     "细菌的结构与繁殖",
     "基础科学知识点内容（人话接口）", "生物学",
     "细菌是单细胞**原核生物**——与动植物细胞的最大区别：**没有成形的细胞核**"
     "（只有 DNA 集中的核区/拟核，无核膜包被）；基本结构：细胞壁、细胞膜、细胞"
     "质、DNA 集中区，有的还有荚膜（保护）、鞭毛（运动）、芽孢（休眠体——极耐高"
     "温干燥，煮沸杀不死需高压蒸汽灭菌）。繁殖：**分裂生殖**（约 20-30 分钟一代"
     "——速度惊人，一个细菌 10 小时可增殖上亿）。营养方式：多数异养（腐生分解"
     "者或寄生致病），少数自养（硝化细菌）。与人类：有益（酸奶乳酸菌/肠道菌群/"
     "根瘤菌/生产胰岛素的大肠杆菌）、有害（结核/霍乱/破伤风）。杀菌原理：高温高"
     "压灭菌锅/抗生素（破坏细胞壁或蛋白质合成）。细菌细胞壁成分与植物不同（肽聚"
     "糖），所以青霉素只抑细菌不伤植物。",
     ["细菌和动植物细胞的主要区别", "细菌靠什么繁殖", "芽孢是什么",
      "细菌是原核生物吗", "细菌对人类有益的例子", "为什么煮沸不能杀死所有细菌"],
     ["问革兰氏染色", "问肠道菌群研究"],
     "atomic", "",
     "细菌=单细胞原核生物(无成形细胞核·拟核)：分裂生殖 20-30min/代·芽孢耐高温；结构=壁膜质+DNA 区+荚膜鞭毛；益=乳酸菌根瘤菌大肠杆菌工程菌/害=结核霍乱。"),
    ("kp_card_typhoon",
     "台风：热带海洋的巨型风暴",
     "人文通识知识点内容（人话接口）", "地理学",
     "台风是生成于热带海洋上的强烈热带气旋（西北太平洋称台风，大西洋/东北太平洋"
     "称飓风——同一现象不同名字）。形成条件：广阔暖海面（海水温度 ≥26.5℃）、充"
     "足水汽、初始扰动、地转偏向力（纬度 ≥5° 才能形成旋转——赤道上不生成）。中"
     "国影响：主要集中在**东南沿海**（广东/台湾/福建/海南/浙江），**夏秋季节**"
     "（7-10 月最频）；台风带来狂风（12 级+）、暴雨（单日可达上千毫米）、风暴潮"
     "（海水倒灌）三重灾害；但也有利：缓解伏旱高温、补充淡水资源。防御：提前预"
     "报（气象卫星/雷达）、渔船回港、加固门窗、低洼转移；台风预警信号蓝黄橙红四"
     "级。命名：14 个国家地区各提供名字循环使用（如「山竹」「利奇马」），造成重"
     "大灾害的名字会被除名。",
     ["台风主要影响中国哪些地区", "台风是怎么形成的", "台风和飓风的区别",
      "台风预警信号等级", "台风有什么好处", "台风的名字怎么来的"],
     ["问台风结构风眼", "问防灾减灾体系"],
     "atomic", "",
     "台风=热带气旋(≥26.5℃ 暖海+水汽+地转偏向力)：影响东南沿海夏秋(7-10 月)；三灾=狂风暴雨风暴潮；益=解伏旱补水；预警蓝黄橙红；重灾名除名循环。"),
]

QUESTIONS = [
    ("QB-469", "超导体有什么特性", "物理学", "技术直答",
     ["零电阻"], "通识拓展84"),
    ("QB-470", "元素分为哪三类", "化学", "技术直答",
     ["金属", "非金属", "稀有气体"], "通识拓展84"),
    ("QB-471", "细菌和动植物细胞的主要区别", "生物学", "技术直答",
     ["无成形细胞核", "原核"], "通识拓展84"),
    ("QB-472", "台风主要影响中国哪些地区", "地理学", "技术直答",
     ["东南沿海", "夏秋"], "通识拓展84"),
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
                               "level:L2", "status:verified", "batch:通识拓展84"],
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
    bank["version"] = "v1.76"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
