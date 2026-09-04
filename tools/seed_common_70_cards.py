# -*- coding: utf-8 -*-
"""seed_common_70_cards.py · 通识拓展批次70知识卡+题库（幂等）

70：物理学-杠杆平衡条件/化学-工业炼铁/生物学-消化系统/生活常识-中暑处理
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_leverbal",
     "杠杆的平衡条件",
     "基础科学知识点内容（人话接口）", "物理学",
     "杠杆平衡条件（杠杆原理）：动力×动力臂=阻力×阻力臂（F₁L₁=F₂L₂）。五要素："
     "支点（O）、动力（F₁）、阻力（F₂）、动力臂（L₁=支点到动力作用线距离）、阻"
     "力臂（L₂）。三类杠杆：省力杠杆（动力臂长：撬棒/瓶起子/老虎钳——省力费距"
     "离）；费力杠杆（动力臂短：筷子/镊子/钓鱼竿——费力省距离，换来操作方便）；"
     "等臂杠杆（天平——不省不费）。阿基米德名言「给我一个支点，我能撬动整个地"
     "球」说的就是省力杠杆的威力——但撬动距离也按同样比例放大，宇宙级杠杆只存在"
     "于思想实验。剪刀是双杠杆；指甲刀是「杠杆+杠杆」复合。计算示例：撬棒动力臂 "
     "1.5m、阻力臂 0.3m，撬 500N 石头只需 F=500×0.3/1.5=100N。",
     ["杠杆的平衡条件是什么", "省力杠杆和费力杠杆的例子", "杠杆五要素",
      "为什么筷子是费力杠杆", "天平是什么杠杆", "给我一个支点撬动地球"],
     ["问杠杆最小力作图", "问滑轮组综合计算"],
     "atomic", "",
     "杠杆平衡 F₁L₁=F₂L₂：省力(撬棒/起子·费距)/费力(筷子/镊子·省距)/等臂(天平)；阿基米德支点名言=省力杠杆思想实验；撬 500N 石头 1.5:0.3 杆只需 100N。"),
    ("kp_card_ironsmelt",
     "工业炼铁的原理",
     "基础科学知识点内容（人话接口）", "化学",
     "工业炼铁在高炉中进行，原理是**还原反应**：一氧化碳（CO）在高温下把铁从氧"
     "化铁里还原出来——3CO + Fe₂O₃ →(高温) 2Fe + 3CO₂（CO 是「还原剂」，夺得氧；"
     "Fe₂O₃ 是被还原）。原料：铁矿石（赤铁矿 Fe₂O₃）、焦炭（燃烧供热+生成 CO："
     "CO₂+C→(高温)2CO）、石灰石（把脉石杂质变成炉渣除去）、空气。产物：生铁（含"
     "碳 2%-4.3%，脆）→进一步炼钢降碳（转炉吹氧）得钢（韧）。实验室对照：用 CO"
     " 或 H₂/C 还原氧化铁粉末（装置尾气要点燃处理防 CO 污染）。古法：中国春秋晚"
     "期已掌握生铁冶炼，早于欧洲约 2000 年。",
     ["工业炼铁的原理", "炼铁的化学方程式", "高炉炼铁的原料",
      "生铁和钢的区别", "石灰石在炼铁中起什么作用", "一氧化碳是还原剂吗"],
     ["问转炉炼钢降碳", "问实验室 CO 还原装置"],
     "atomic", "",
     "炼铁=CO 高温还原 Fe₂O₃(3CO+Fe₂O₃→2Fe+3CO₂·CO 为还原剂)；料=铁矿+焦炭(供热产 CO)+石灰石(造渣)；产物生铁(碳高脆)→转炉降碳成钢；中国春秋已冶生铁。"),
    ("kp_card_digestsys",
     "消化系统的组成",
     "基础科学知识点内容（人话接口）", "生物学",
     "消化系统=**消化道**+**消化腺**两部分。消化道（食物经过的管道，自上而下）："
     "口腔→咽→食道→胃→小肠→大肠→肛门。消化腺：唾液腺（唾液淀粉酶初步消化淀"
     "粉）、肝脏（最大消化腺，分泌胆汁乳化脂肪）、胰腺（胰液含多种消化酶）、胃"
     "腺（胃液含胃蛋白酶+盐酸）、肠腺（肠液）。**小肠**是消化和吸收的主要场所："
     "长约 5-6 米、内表面皱襞+小肠绒毛使吸收面积巨大（可达 200㎡）、绒毛壁薄（一"
     "层上皮细胞）且密布毛细血管。三大营养物质的消化：淀粉→麦芽糖→葡萄糖（口"
     "腔开始）；蛋白质→氨基酸（胃开始）；脂肪→甘油+脂肪酸（只在小肠，靠胆汁乳"
     "化+酶分解）。无消化功能的部分：大肠只吸收少量水/无机盐/部分维生素。",
     ["人体消化系统由什么组成", "消化和吸收的主要场所", "小肠为什么吸收面积大",
      "三大营养物质的消化过程", "大肠有什么功能", "胆汁不含消化酶为什么重要"],
     ["问消化酶一览表", "问阑尾炎位置"],
     "atomic", "",
     "消化系统=消化道(口咽食道胃小肠大肠肛门)+消化腺(唾液/肝/胰/胃/肠腺)；小肠=消化吸收主场所(5-6m·绒毛 200㎡)；淀粉口腔始/蛋白胃始/脂肪只在小肠；大肠只吸水盐维素。"),
    ("kp_card_heatstroke",
     "中暑的处理与预防",
     "生活常识知识点内容（人话接口）", "生活常识",
     "中暑：高温高湿环境下身体散热失败——轻症（先兆/轻症中暑）：头晕口渴大汗乏"
     "力；重症：热痉挛/热衰竭/热射病（核心体温超 40℃、意识障碍——**致死率高，"
     "必须立即送医**）。现场处理「移、降、补」：①移——迅速搬到阴凉通风处，平躺"
     "抬高双脚；②降——解开衣物、湿毛巾擦身/扇风/冰袋敷颈侧腋下腹股沟（大血管"
     "处）；③补——清醒者少量多次喝淡盐水/运动饮料（昏迷者**禁止喂水**防呛窒"
     "息）。预防：避开正午高温时段外出、戴帽防晒、每 15-20 分钟补水（大量出汗补"
     "含盐饮料而非纯水——防低钠）、老人幼儿高温天不开空调是中暑高危因素（独居老"
     "人热射病多见）。车内高温致死：儿童绝不可单独留在车内（封闭车厢 15 分钟可"
     "达 50℃+）。",
     ["中暑了怎么办", "热射病是什么", "昏迷的中暑者能喂水吗",
      "怎么预防中暑", "为什么不能把孩子单独留在车里", "冰敷敷在哪里降温快"],
     ["问热射病分型诊断", "问空调病话题"],
     "atomic", "",
     "中暑处理=移阴凉+降体温(冰敷颈腋股)+补水盐(**昏迷禁喂水**)；热射病>40℃ 意识障碍致死率高速送医；预防=避正午/补含盐水/老人幼儿高危；车内 15min 可 50℃ 勿留人。"),
]

QUESTIONS = [
    ("QB-413", "杠杆的平衡条件是什么", "物理学", "技术直答",
     ["F1L1", "动力", "阻力臂"], "通识拓展70"),
    ("QB-414", "工业炼铁的原理", "化学", "技术直答",
     ["一氧化碳", "还原", "氧化铁"], "通识拓展70"),
    ("QB-415", "人体消化系统由什么组成", "生物学", "技术直答",
     ["消化道", "消化腺"], "通识拓展70"),
    ("QB-416", "中暑了怎么办", "生活常识", "技术直答",
     ["阴凉", "降温", "补水"], "通识拓展70"),
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
                               "level:L2", "status:verified", "batch:通识拓展70"],
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
    bank["version"] = "v1.62"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
