# -*- coding: utf-8 -*-
"""seed_common_52_cards.py · 通识拓展批次52知识卡+题库（幂等）

52：物理学-太阳能电池/化学-食醋与水垢/生物学-肝脏与消化/历史-半坡与河姆渡
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_solarcell",
     "太阳能电池：光生伏特效应",
     "基础科学知识点内容（人话接口）", "物理学",
     "太阳能电池板把光能直接转化为电能（光生伏特效应，不是「烧水发电」那种间"
     "接方式）：核心是半导体 PN 结——光子打入硅半导体，激发出电子-空穴对，被内"
     "建电场分离形成电流。材料以晶体硅为主（单晶硅效率约 20%+，多晶硅略低）；新"
     "型钙钛矿电池效率飙升中。优点：清洁无排放、取之不尽（到达地球 1 小时的阳光"
     "≈全球一年能耗）；局限：夜间/阴天不发电需储能（配蓄电池）、能量密度低（占"
     "地）。中国是全球最大光伏生产与装机国（2023 年累计装机超 600GW）。相关：太"
     "阳能热水器=把光能转成热能（集热管），与电池板原理不同——常考辨析。",
     ["太阳能电池板把什么能转化为什么能", "太阳能电池的原理", "光伏发电是什么意思",
      "太阳能热水器是怎么工作的", "光伏发电的优缺点", "中国光伏产业世界第几"],
     ["问PN结半导体物理", "问储能电池配套"],
     "atomic", "",
     "太阳能电池=光能→电能(光生伏特·PN结·晶体硅约20%+)；优点清洁无限/局限需储能占地；中国光伏装机全球第一；热水器=光→热(集热)与光伏不同。"),
    ("kp_card_vinegar",
     "食醋除水垢的原理",
     "生活常识知识点内容（人话接口）", "化学",
     "水壶里的白色硬垢主要成分是碳酸钙（CaCO₃）和氢氧化镁——来自水中钙镁化合物"
     "受热分解沉淀。食醋能除垢：醋酸（乙酸，CH₃COOH，食醋约 3-5%）是酸，与碳酸"
     "钙反应生成可溶的醋酸钙+水+二氧化碳（冒泡）——「酸溶钙」。操作：白醋加水"
     "浸泡煮沸静置几小时，倒出清水冲洗；柠檬酸同理（更好闻）。拓展：醋的其他用途"
     "同源——软化蔬菜纤维（炒土豆丝爽脆）、去腥（与胺类反应）、鸡蛋壳（CaCO₃）"
     "泡醋变软演示酸反应。注意：铝锅不宜久泡醋（铝两性金属酸碱都蚀）。",
     ["白醋能除水垢吗", "水垢的主要成分", "醋除水垢的化学方程式",
      "白醋的主要成分是什么", "鸡蛋壳泡醋会怎样", "铝锅为什么不能泡醋"],
     ["问乙酸结构性质", "问硬水软水"],
     "atomic", "",
     "水垢=CaCO₃+Mg(OH)₂；食醋除垢=醋酸溶钙(CaCO₃+酸→可溶醋酸钙+CO₂冒泡)；柠檬酸同理；铝锅忌久泡(两性被蚀)；鸡蛋壳泡醋变软=同款反应。"),
    ("kp_card_liver",
     "肝脏：最大的消化腺",
     "基础科学知识点内容（人话接口）", "生物学",
     "肝脏是人体最大的消化腺（也是最大的内脏器官，重约 1.5 公斤，位于右上腹、"
     "肋骨后面）。消化功能：分泌胆汁——胆汁不含消化酶，但能把大脂肪球**乳化**成"
     "小脂肪滴（增大脂肪酶的作用面积，帮助脂肪消化）；胆囊储存浓缩胆汁，吃油腻食"
     "物时排出（胆囊炎者忌油腻）。肝脏还有五百多种功能：解毒（酒精/药物代谢工厂"
     "——所以长期饮酒伤肝）、储存糖原（调节血糖）、合成血浆蛋白等。肝脏再生能力"
     "惊人（切掉部分可再生长）但「沉默器官」——内部无痛觉神经，肝病早期常无痛感"
     "，体检查肝功能很重要。消化腺全家：唾液腺/肝脏/胰腺/胃腺/肠腺。",
     ["人体最大的消化腺是什么", "胆汁是由哪个器官分泌的", "胆汁含消化酶吗",
      "肝脏有哪些功能", "为什么说肝脏是沉默的器官", "喝酒为什么伤肝"],
     ["问胰液肠液分工", "问脂肪消化全链路"],
     "atomic", "",
     "肝脏=最大消化腺+最大内脏(约1.5kg·右季肋区)：分泌胆汁(无酶·乳化脂肪)·解毒/储糖原/合成蛋白；再生强但无痛觉神经(沉默器官)；胆囊只储存浓缩。"),
    ("kp_card_banpo",
     "半坡与河姆渡：农耕文明的开端",
     "人文通识知识点内容（人话接口）", "历史",
     "中国新石器时代的两大农耕文明代表（距今约六七千年）：①半坡居民（黄河流"
     "域，陕西西安半坡遗址）——住半地穴式房屋（保暖），种植**粟**（小米，黄河流"
     "域最早栽培），养猪狗，用彩陶（人面鱼纹盆是国宝）；②河姆渡居民（长江流域，"
     "浙江余姚河姆渡遗址）——住干栏式房屋（防潮防虫，上层住人），种植**水稻**"
     "（世界最早栽培水稻之一），驯化水牛，用黑陶和骨耜。「南稻北粟」格局由此确"
     "立——中国是世界农业起源中心之一（水稻/粟/大豆均原产中国）。两遗址共同证"
     "明：中国农耕文明独立起源、南北并立，不是单点传播。",
     ["半坡人种植什么作物", "河姆渡人住什么房屋", "南稻北粟是什么意思",
      "人面鱼纹盆出土于哪里", "干栏式建筑的特点", "中国最早种植的水稻在哪里"],
     ["问良渚仰韶对比", "问新石器农业传播"],
     "atomic", "",
     "半坡(黄河·西安)=半地穴+种粟+彩陶(人面鱼纹盆)；河姆渡(长江·余姚)=干栏式+种水稻(世界最早之一)+黑陶骨耜；「南稻北粟」确立；中国=农业起源中心。"),
]

QUESTIONS = [
    ("QB-341", "太阳能电池板把什么能转化为什么能", "物理学", "技术直答",
     ["光能", "电能"], "通识拓展52"),
    ("QB-342", "白醋能除水垢吗", "化学", "技术直答",
     ["能", "醋酸", "碳酸钙"], "通识拓展52"),
    ("QB-343", "人体最大的消化腺是什么", "生物学", "技术直答",
     ["肝脏"], "通识拓展52"),
    ("QB-344", "半坡人种植什么作物", "历史", "技术直答",
     ["粟", "小米"], "通识拓展52"),
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
                               "level:L2", "status:verified", "batch:通识拓展52"],
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
    bank["version"] = "v1.44"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
