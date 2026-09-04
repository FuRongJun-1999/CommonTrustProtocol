# -*- coding: utf-8 -*-
"""seed_common_64_cards.py · 通识拓展批次64知识卡+题库（幂等）

64：物理学-水的比热容/化学-糖类/生物学-无土栽培/生活常识-保质期与保存期
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_cwater",
     "水的比热容：海边昼夜温差小",
     "基础科学知识点内容（人话接口）", "物理学",
     "比热容（c）=单位质量物体温度升高 1℃ 吸收的热量（Q=cmΔt）——水的比热容"
     "是 4.2×10³ J/(kg·℃)，在常见物质中最大（约是沙石的 4-5 倍）。生活与自然"
     "解释：①海边昼夜温差小、内陆沙漠温差大（白天海水升温慢吸走热量、夜里放热"
     "慢——天然空调）；②城市有湖/绿地更凉爽（水体调节）；③汽车发动机用水做冷"
     "却液、暖气用水做传热介质（同样吸放热温度变化小、载热多）；④早稻育秧傍晚"
     "灌水夜间护秧（水保温）。计算示例：1kg 水升 1℃ 吸 4200J；同热量下沙石升"
     "温约是水的 4-5 倍。比热容是物质的特性（与质量形状无关），常见中只有水最大"
     "——「水的比热容大」是中考热学万能解释句。",
     ["为什么海边昼夜温差小", "水的比热容是多少", "汽车水箱为什么用水",
      "比热容的公式", "什么是热平衡", "育秧为什么要傍晚灌水"],
     ["问热平衡方程计算", "问其他高比热物质"],
     "atomic", "",
     "比热容 c=Q/(mΔt)：水 4.2×10³ J/(kg·℃) 最大——海边温差小/水箱冷却液/傍晚灌水护秧皆是它；同热下沙石升温 4-5 倍；物质特性与质量无关。"),
    ("kp_card_carbo",
     "糖类：人体的主燃料",
     "基础科学知识点内容（人话接口）", "化学",
     "糖类（碳水化合物）由 C、H、O 三种元素组成，是人体最主要的供能物质（供能"
     "约占 60-70%）。家族：①单糖——葡萄糖（直接被吸收，血糖就是它，医学上「葡"
     "萄糖耐量」测糖尿病）；②二糖——蔗糖（白糖）、麦芽糖（饴糖）、乳糖（奶"
     "中）；③多糖——淀粉（主食成分）与糖原（肝糖原/肌糖原，人体储能）。转化链："
     "淀粉→麦芽糖→葡萄糖→氧化供能（CO₂+H₂O）或合成糖原储存。过量危害：多余糖"
     "转化为脂肪（肥胖）、血糖长期过高损伤血管（糖尿病）。低血糖症状：心慌/出"
     "汗/头晕——立即吃糖块缓解。膳食纤维（纤维素）也是糖类但人体不消化——促进"
     "肠道蠕动，被称为「第七大营养素」。",
     ["糖类包括哪些", "血糖指的是什么糖", "淀粉在人体内怎么消化",
      "低血糖了怎么办", "糖原是什么", "膳食纤维能消化吗"],
     ["问糖化学式对比", "问无糖食品原理"],
     "atomic", "",
     "糖类(C·H·O)=主供能 60-70%：单糖(葡萄糖=血糖)/二糖(蔗糖麦芽乳糖)/多糖(淀粉·糖原储能)；链=淀粉→麦芽糖→葡萄糖；过量转脂肪；纤维素=第七营养素不消化。"),
    ("kp_card_hydroponic",
     "无土栽培与营养液",
     "基础科学知识点内容（人话接口）", "生物学",
     "无土栽培不用土壤，把植物种在营养液中（或基质+营养液）——根系直接吸收溶解"
     "在水里的矿质元素。营养液按比例含有植物所需的全部矿质营养：大量元素（氮磷"
     "钾钙镁硫）+微量元素（铁锰硼锌铜钼氯镍）。优点：①不受土壤限制（沙漠/楼"
     "顶/太空站都能种——国际空间站生菜）；②产量高品质可控（水肥精准供给）；③"
     "无土传病虫害、省水省肥（循环利用）。方式：水培（根系泡液+增氧泵）、雾培（"
     "根系喷营养雾）、基质培（岩棉/椰糠持液）。植物从土里主要吸收的是水分和无机"
     "盐（土壤只起固定+保水供肥作用）——这是无土栽培可行的理论依据。家庭版：水"
     "培绿萝/风信子即是简化无土栽培。",
     ["无土栽培用什么代替土壤", "营养液里有什么", "无土栽培有什么优点",
      "植物从土壤里吸收什么", "太空站怎么种菜", "水培绿萝的原理"],
     ["问植物必需元素清单", "问农业无土栽培案例"],
     "atomic", "",
     "无土栽培=营养液替代土壤：含大量元素(NPK Ca Mg S)+微量元素(Fe Mn B 等)；优势=不限场地/高产/无土传病害/省水肥；理论=土壤只起固定与供肥作用；空间站同款。"),
    ("kp_card_shelflife",
     "保质期与保存期的区别",
     "生活常识知识点内容（人话接口）", "生活常识",
     "保质期：预包装食品在标签指明的贮存条件下保持**品质**的期限（在此期内厂家"
     "承诺风味口感品质达标）；保存期：食品的**最后食用日期**——过了保存期就不"
     "能吃了。区别一句话：保质期内保证品质最佳，超过保质期不一定变质但厂家不再"
     "担保（法律上也不允许再销售）；超过保存期绝对不能吃。贮存条件是前提：「常温"
     "避光」的鲜奶开了冷藏、写了「冷藏」的酸奶放在常温——保质期作废。没有保质"
     "期的例外：酒精（10 度以上饮料酒）、醋、盐、糖、味精可免标（不易变质）。过"
     "期食品风险：微生物超标/油脂酸败（哈喇味）/营养流失——宁弃勿食。网购临期"
     "食品要看清日期与贮存要求。",
     ["保质期和保存期的区别", "过期食品还能吃吗", "贮存条件重要吗",
      "哪些食品可以不标保质期", "临期食品能买吗", "食用油过期会怎样"],
     ["问食品标签法规", "问防腐技术史"],
     "atomic", "",
     "保质期=品质最佳期限(过期不担保不可售)vs 保存期=最后食用期(过期必弃)；前提=贮存条件(酸奶常温→作废)；免标=高度酒/醋/盐/糖；风险=菌超标/酸败哈喇味。"),
]

QUESTIONS = [
    ("QB-389", "为什么海边昼夜温差小", "物理学", "技术直答",
     ["比热容", "水"], "通识拓展64"),
    ("QB-390", "糖类包括哪些", "化学", "技术直答",
     ["淀粉", "葡萄糖", "蔗糖"], "通识拓展64"),
    ("QB-391", "无土栽培用什么代替土壤", "生物学", "技术直答",
     ["营养液"], "通识拓展64"),
    ("QB-392", "保质期和保存期的区别", "生活常识", "技术直答",
     ["品质", "最后食用日期"], "通识拓展64"),
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
                               "level:L2", "status:verified", "batch:通识拓展64"],
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
    bank["version"] = "v1.56"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
