# -*- coding: utf-8 -*-
"""seed_common_98_cards.py · 通识拓展批次98知识卡+题库（幂等）

98：物理学-重力/化学-元素符号的意义/生物学-毒品的危害/地理学-高新技术产业
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_gravity",
     "重力：G=mg",
     "基础科学知识点内容（人话接口）", "物理学",
     "重力：地球对物体的吸引力（源于万有引力）——三要素：①大小 **G=mg**（g=9.8"
     "N/kg，粗略计算取 10——质量 1kg 的物体重约 9.8N）；②方向——**竖直向下**（指"
     "向地心，不是「垂直向下」——垂直于支撑面可能倾斜）；③作用点——**重心**（质"
     "量分布的中心：均匀规则物体在几何中心，不倒翁重心低所以不倒）。应用：重垂"
     "线（检查墙壁是否竖直）、水平仪。重力与质量的区别：质量是物体所含物质的多少"
     "（kg，不变），重力是一种力（N，随 g 变化——月球上质量不变但重力约为地球的"
     "1/6，所以宇航员月球上跳得高）。g 值随纬度升高略增、随海拔升高略减。",
     ["重力的大小方向作用点", "G=mg是什么意思", "重力与质量的区别",
      "不倒翁为什么不倒", "月球上重力是地球的几分之一", "重垂线的用途"],
     ["问重心确定方法", "问万有引力与重力的关系"],
     "atomic", "",
     "重力 G=mg(g=9.8N/kg)：方向竖直向下(非垂直)·作用点=重心(不倒翁低重心)；质量 kg 不变 vs 重力 N 随 g 变(月球 1/6)；应用=重垂线/水平仪。"),
    ("kp_card_elemsym",
     "元素符号的意义",
     "基础科学知识点内容（人话接口）", "化学",
     "元素符号（如 H、O、C、Fe）通常表示三层意义：①表示**一种元素**（宏观——氢"
     "元素）；②表示这种元素的**一个原子**（微观——一个氢原子）；③由原子直接构"
     "成的物质（金属/稀有气体/固态非金属如铁、氦、碳），符号还表示**该物质**（Fe"
     " 既表示铁元素、一个铁原子，也表示铁这种物质）。附加意义：加数字表示原子个"
     "数——2H=2 个氢原子（只微观）、2H₂=2 个氢分子。书写规范：一大二小（Ca 不能"
     "写成 CA、Co 是钴而 CO 是一氧化碳——顺序错则意义全变）。元素符号是国际通用"
     "语言（源于拉丁文——钠 Na/Natrium、金 Au/Aurum、铁 Fe/Ferrum）。",
     ["元素符号表示什么", "元素符号的书写规范", "2H和H₂的区别",
      "CO和Co有什么区别", "元素符号来源于什么语言", "Fe表示哪些意义"],
     ["问化学式意义对比", "问元素周期表符号来源"],
     "atomic", "",
     "元素符号三层义=一种元素(宏观)+一个原子(微观)+原子直接构成的物质；前加数字只表原子个数(2H)；书写一大二小(Co 钴≠CO 一氧化碳)；源自拉丁文国际通用。"),
    ("kp_card_drugharm",
     "毒品的危害与拒绝",
     "生活常识知识点内容（人话接口）", "生活常识",
     "毒品指鸦片、海洛因、甲基苯丙胺（冰毒）、吗啡、大麻、可卡因以及国家规定管"
     "制的其他能使人形成瘾癖的麻醉药品和精神药品。危害三层：①毁自己——损害中枢"
     "神经与免疫（精神依赖极强、戒断极难），身体衰竭、感染艾滋病（共用注射器）"
     "；②害家庭——倾家荡产、家庭破裂；③危害社会——诱发犯罪、危害公共安全。新型"
     "毒品伪装性强：「奶茶粉」「跳跳糖」「电子烟油」形态出现——不接受陌生人给的食"
     "物饮料、离席后不再饮用已开饮品。国际禁毒日 6 月 26 日；虎门销烟（1839）是中"
     "国禁毒史的丰碑。法律：《刑法》规定走私/贩卖/运输/制造毒品无论数量多少都追"
     "究刑事责任。拒毒三招：不接受、不好奇、不侥幸（「吸一口不会上瘾」是致命误"
     "解）。",
     ["毒品的危害", "新型毒品有哪些伪装", "国际禁毒日是哪天",
      "虎门销烟和禁毒的关系", "怎么拒绝毒品", "吸毒会感染艾滋病吗"],
     ["问禁毒法体系", "问戒毒医学方法"],
     "atomic", "",
     "毒品=麻醉/精神药品致瘾癖：毁自己(神经免疫·共用针具染艾滋)+害家庭+危害社会；新型毒品伪装奶茶跳跳糖——不接受不侥幸；6.26 禁毒日；虎门销烟=禁毒丰碑。"),
    ("kp_card_hightech",
     "高新技术产业",
     "人文通识知识点内容（人话接口）", "地理学",
     "高新技术产业：以电子和信息类产业为「龙头」的产业（科技含量高、更新换代"
     "快、研发人员占比高）。中国布局：**沿海——科技园区型**（京津冀：北京中关村"
     "——中国第一个国家级高新区「中国硅谷」；长三角：上海张江；珠三角：深圳——"
     "腾讯/华为/大疆）；**沿边——贸易导向型**（边境口岸）；**内陆——军工开发型"
     "**（西安/成都的航空航天）。特点：从业人员中科技人员比重大、研发投入高、产"
     "品更新快、附加值高、对自然资源依赖小（不同于传统资源型工业）。中口「十四五"
     "」重点：集成电路（芯片）、人工智能、量子信息、生物医药、新能源。分布逻辑："
     "靠近高校科研院所（人才）+交通便捷+环境优美——与技术、人才高度正相关，与原"
     "料产地关系减弱。",
     ["高新技术产业的特点", "中关村的地位", "中国高新技术产业分布",
      "高新技术产业和传统工业的区别", "为什么高新区靠近大学", "深圳的高新技术产业"],
     ["问硅谷与中国硅谷对比", "问专精特新企业"],
     "atomic", "",
     "高新技术产业=电子信息为龙头：科技人员比重高/研发投入大/更新快/附加值高/少依赖资源；布局=沿海科技园区(中关村「中国硅谷」·深圳)+内陆军工型；区位靠人才与交通。"),
]

QUESTIONS = [
    ("QB-525", "重力的大小方向作用点", "物理学", "技术直答",
     ["G=mg", "竖直向下", "重心"], "通识拓展98"),
    ("QB-526", "元素符号表示什么", "化学", "技术直答",
     ["元素", "一个原子"], "通识拓展98"),
    ("QB-527", "毒品的危害", "生活常识", "技术直答",
     ["神经", "家庭", "社会"], "通识拓展98"),
    ("QB-528", "高新技术产业的特点", "地理学", "技术直答",
     ["科技人员", "研发", "附加值"], "通识拓展98"),
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
                               "level:L2", "status:verified", "batch:通识拓展98"],
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
    bank["version"] = "v1.90"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
