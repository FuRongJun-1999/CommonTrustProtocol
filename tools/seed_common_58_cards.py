# -*- coding: utf-8 -*-
"""seed_common_58_cards.py · 通识拓展批次58知识卡+题库（幂等）

58：物理学-运动静止的相对性/化学-合成材料/生物学-植物的组织/地理学-中国湖泊之最
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_reference",
     "运动和静止的相对性",
     "基础科学知识点内容（人话接口）", "物理学",
     "判断一个物体是运动还是静止，取决于选什么物体做**参照物**：坐在行驶的火车"
     "里，以车厢为参照物你是静止的；以地面为参照物你是运动的——运动和静止是相对"
     "的。经典案例：「小小竹排江中游，巍巍青山两岸走」（青山「走」是以竹排为参照"
     "物）；空中加油机与受油机相对静止；地球同步卫星相对地面静止、相对太阳运"
     "动。参照物选择原则：任意性（研究方便即可，但不选研究对象自身）；通常默认地"
     "面。宇宙中没有绝对不动的物体——运动是绝对的，静止是相对的。应用：接力赛"
     "交接棒要相对静止才稳、空中揽收航天器对接（毫秒级相对静止控制）。",
     ["坐在行驶的车里是运动还是静止", "什么是参照物", "运动和静止为什么是相对的",
      "同步卫星相对什么静止", "空中加油的原理", "青山两岸走是什么参照物"],
     ["问速度计算", "问相对论时空观科普"],
     "atomic", "",
     "运动/静止取决于参照物(车厢静·地面动)；参照物任意选(不选自身·默认地面)；竹排青山/加油机/同步卫星皆相对性例；运动绝对·静止相对。"),
    ("kp_card_synthetic",
     "合成材料：塑料合成纤维合成橡胶",
     "基础科学知识点内容（人话接口）", "化学",
     "有机合成材料三大类：①塑料——聚乙烯（保鲜膜/袋）、聚氯乙烯（PVC 管道）、"
     "聚苯乙烯（泡沫餐盒）等，可塑性强但难降解（白色污染——推行限塑/可降解塑"
     "料）；②合成纤维——涤纶（的确良）、锦纶（尼龙）、腈纶（人造毛），强度高"
     "耐磨但透气性差（烧后结硬球，与棉烧焦毛味区分）；③合成橡胶——轮胎/密封"
     "件（比天然橡胶更耐油耐老化）。与之相对：天然材料（棉花/羊毛/蚕丝/天然橡胶"
     "）；天然纤维烧后有烧纸/焦毛味、灰可捻碎——鉴别纤维的经典方法。材料家族总"
     "览：金属材料/无机非金属材料（陶瓷玻璃水泥）/有机合成材料/复合材料（玻璃"
     "钢、钢筋混凝土、碳纤维——优势组合）。",
     ["塑料是天然材料吗", "合成材料有哪三大类", "涤纶和棉怎么区分",
      "什么是白色污染", "什么是复合材料", "聚乙烯和聚氯乙烯的区别"],
     ["问高分子化学基础", "问可降解塑料原理"],
     "atomic", "",
     "三大合成材料=塑料(PE/PVC·白色污染)+合成纤维(涤纶锦纶腈纶·烧结硬球)+合成橡胶(轮胎)；vs 天然材料(棉毛丝烧焦毛味)；复合材料=玻璃钢/碳纤维。"),
    ("kp_card_planttissue",
     "植物的五大组织",
     "基础科学知识点内容（人话接口）", "生物学",
     "植物体的主要组织（由形态相似功能相同的细胞群构成）：①分生组织——终生保持"
     "分裂能力（根尖/芽顶端），是植物「长长长粗」的源头；②保护组织——表皮（叶"
     "表皮/根冠外层），保护内部减少水分散失；③营养组织——叶肉/果肉，细胞壁薄液"
     "泡大，含叶绿体行光合作用、储存营养；④输导组织——导管（自下而上运水无机"
     "盐，死细胞连成的管道）与筛管（自上而下运有机物，活细胞）；⑤机械组织——"
     "厚壁细胞支撑加固（茎秆纤维）。动物组织对比：上皮/结缔/肌肉/神经四大组织——"
     "动植物组织分类不同是常考辨析。叶是最能体现分工的器官：表皮（保护）+叶肉（"
     "营养·光合）+叶脉（输导）。",
     ["植物的五大组织是什么", "导管和筛管的区别", "分生组织在哪里",
      "叶肉属于什么组织", "动物有哪四大组织", "叶的结构对应什么组织"],
     ["问植物器官六大件", "问导管毛细现象补充"],
     "atomic", "",
     "植物五组织=分生(分裂·根尖芽)/保护(表皮)/营养(叶肉果肉·光合)/输导(导管上行水盐·筛管下行有机物)/机械(支撑)；动物四组织=上皮结缔肌肉神经。"),
    ("kp_card_lakes",
     "中国湖泊之最",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国湖泊之最：最大的淡水湖=鄱阳湖（江西，丰水期约 3000+ 平方公里，长江"
     "「调节器」，候鸟天堂）；第二大淡水湖=洞庭湖（湖南，「洞庭天下水」，昔日八"
     "百里洞庭因围湖造田缩小——退田还湖在进行）；最大的湖（也是最大咸水湖）=青"
     "海湖（约 4600 平方公里，内流湖）；海拔最高的湖=纳木错（西藏，约 4718 米，"
     "咸水湖）；最深的湖在国境之外（贝加尔湖），中国最深火山湖=长白山天池。湖泊"
     "成因多样：构造湖（青海湖/滇池）、火山口湖（天池）、堰塞湖（五大连池）、河"
     "迹湖（洞庭——长江改道遗迹）。淡水湖集中于长江中下游（「五湖」：鄱阳/洞庭/"
     "太湖/洪泽/巢湖）。",
     ["中国最大的淡水湖是哪个", "中国最大的咸水湖", "洞庭湖为什么变小了",
      "海拔最高的湖是哪个", "长白山天池是怎么形成的", "中国五大淡水湖"],
     ["问湿地生态价值", "问湖泊萎缩治理"],
     "atomic", "",
     "湖泊之最：最大淡水=鄱阳湖(江西)·次=洞庭湖(围湖缩小·退田还湖)；最大湖+最大咸水=青海湖；最高=纳木错(4718m)；最深=长白山天池(火山口)；成因四型。"),
]

QUESTIONS = [
    ("QB-365", "坐在行驶的车里是运动还是静止", "物理学", "技术直答",
     ["参照物", "相对"], "通识拓展58"),
    ("QB-366", "塑料是天然材料吗", "化学", "技术直答",
     ["不是", "合成材料"], "通识拓展58"),
    ("QB-367", "植物的五大组织是什么", "生物学", "技术直答",
     ["分生", "保护", "营养", "输导", "机械"], "通识拓展58"),
    ("QB-368", "中国最大的淡水湖是哪个", "地理学", "技术直答",
     ["鄱阳湖"], "通识拓展58"),
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
                               "level:L2", "status:verified", "batch:通识拓展58"],
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
    bank["version"] = "v1.50"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
