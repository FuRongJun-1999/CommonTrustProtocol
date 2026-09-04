# -*- coding: utf-8 -*-
"""seed_common_102_cards.py · 通识拓展批次102知识卡+题库（幂等）

102：物理学-热机/化学-油脂/生物学-食品安全/地理学-中国的糖料作物
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_heatengine",
     "热机：内能转化为机械能",
     "基础科学知识点内容（人话接口）", "物理学",
     "热机：把内能转化为机械能的机器（燃料燃烧→工质→做功）。四冲程汽油机一个工"
     "作循环：**吸气→压缩→做功→排气**，活塞往复 2 次、曲轴转 2 圈，只有**做功冲"
     "程**对外做功（内能→机械能）；压缩冲程机械能→内能（温度升高点燃混合气，汽"
     "油机火花塞点燃/柴油机压燃）。热机效率：汽油机约 25-35%、柴油机约 30-45%——"
     "大部分能量以废气/散热/摩擦损耗（机械效率总小于 100%）。种类演进：蒸汽机（"
     "外燃，瓦特改良推动工业革命）→内燃机（汽油机/柴油机）→喷气发动机→火箭。环"
     "保：尾气（CO/氮氧化物/颗粒物）治理+新能源车替代。",
     ["四冲程内燃机的一个工作循环", "热机的效率", "做功冲程的能量转化",
      "汽油机和柴油机的区别", "蒸汽机和内燃机", "热机效率为什么小于100%"],
     ["问压缩比与爆震", "问新能源车替代节奏"],
     "atomic", "",
     "四冲程=吸气→压缩→做功→排气：只有做功冲程内能→机械能·压缩冲程机械→内能；效率汽油 25-35% 柴油更高；演进=蒸汽机(外燃)→内燃机→喷气。"),
    ("kp_card_fatsoil",
     "油脂：人体的备用能源",
     "基础科学知识点内容（人话接口）", "化学",
     "油脂=油（液态，植物来源：花生油/豆油/菜籽油）+脂肪（固态，动物来源：猪"
     "油/奶油），由甘油和脂肪酸构成。功能：①备用能源物质（同质量供能约是糖类的"
     "2 倍——「储能高手」，多余糖类也会转成脂肪储存）；②保温缓冲（皮下脂肪）；"
     "③溶解脂溶性维生素（A/D/E/K）助吸收；④构成细胞膜等结构（磷脂）。健康提醒："
     "摄入过多→肥胖/高血脂/心脑血管疾病；反式脂肪酸（部分氢化植物油——人造奶"
     "油/炸鸡奶油蛋糕）危害更大，应限量。合理膳食：油摄入每天 25-30g（约两三瓷"
     "勺），植物油动物油换着吃。",
     ["油脂的作用是什么", "油和脂肪的区别", "为什么说油脂是备用能源",
      "反式脂肪酸的危害", "每天摄入多少油合适", "脂溶性维生素有哪些"],
     ["问血脂与肥胖机理", "问油脂化学结构"],
     "atomic", "",
     "油脂=油(液·植物)+脂肪(固·动物)·甘油+脂肪酸：备用能源(同质量≈糖 2 倍)+保温+载脂溶维生素；反式脂肪酸害处大；日限 25-30g。"),
    ("kp_card_foodsafety2",
     "食品安全：从购买到入口",
     "生活常识知识点内容（人话接口）", "生活常识",
     "食品安全全链条注意：①**购买**——看生产日期/保质期/贮存条件/SC 编号（生"
     "产许可），不买三无产品与胀袋/漏气/变色食品；②**储存**——生熟分开、冷藏冷"
     "冻按要求（冰箱不是保险箱——listeria 嗜冷菌仍可繁殖）；③**加工**——烧熟煮"
     "透（肉类中心温度 70℃+）、生熟刀具案板分开（防交叉污染）、四季豆/豆浆必须"
     "彻底加热（天然毒素：皂苷/凝集素）；④**外出就餐**——选证照齐全餐厅；⑤**食"
     "物中毒应急**——立即停止食用、催吐并就医、保留样本。天然毒素案例：发芽土豆"
     "（龙葵素）、鲜黄花菜（秋水仙碱）、河豚（河豚毒素）、毒蘑菇（无简单鉴别法——"
     "「不采摘不购买不食用」野菇）。食品安全法与「最严谨标准」监管。",
     ["食品安全需要注意什么", "发芽土豆为什么不能吃", "豆浆为什么要煮熟",
      "毒蘑菇能靠颜色辨别吗", "食物中毒了怎么办", "冰箱是保险箱吗"],
     ["问 HACCP 体系", "问食源性疾病统计"],
     "atomic", "",
     "食品安全链=购买(看日期SC)/储存(生熟分开)/加工(煮熟透·四季豆豆浆有毒蛋白)/就餐；天然毒=发芽土豆龙葵素/鲜黄花菜/毒蘑菇无鉴别法；中毒=停食催吐就医留样。"),
    ("kp_card_sugarcrop",
     "中国的糖料作物：南甘北甜",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国两大糖料作物「**南甘北甜**」：①甘蔗——热带亚热带作物，喜高温多雨，分"
     "布在华南（广西最大产区——产量占全国六成以上、云南/广东/海南），制糖为主；"
     "②甜菜——温带作物，耐寒耐盐碱，分布在北方（黑龙江/新疆/内蒙古），东北是甜"
     "菜糖基地。分布逻辑：糖料作物对热量要求不同——甘蔗喜热只能南方，甜菜耐寒适"
     "合北方（与「南稻北麦」同理：气候决定农业）。历史：中国自古用蜂蜜和饴糖（麦"
     "芽糖），甘蔗制糖唐代从印度传入制糖术而大发展。甜菜糖是近代（20 世纪初东北）"
     "才发展。世界最大产糖国：巴西/印度（甘蔗）。糖料与油料作物并列：油料「南油"
     "（油菜）北花（花生）大豆」。",
     ["中国的糖料作物是什么", "南甘北甜是什么意思", "甘蔗分布在哪些省",
      "甜菜适合什么气候", "广西为什么产糖多", "世界最大产糖国"],
     ["问糖业历史", "问油料作物分布复习"],
     "atomic", "",
     "糖料「南甘北甜」：甘蔗=热带亚热(广西占六成+)制糖；甜菜=温带耐寒(黑新蒙)；逻辑=热量决定；史上蜂蜜饴糖→唐传印制糖术；世界产糖首=巴西印度。"),
]

QUESTIONS = [
    ("QB-541", "四冲程内燃机的一个工作循环", "物理学", "技术直答",
     ["吸气", "压缩", "做功", "排气"], "通识拓展102"),
    ("QB-542", "油脂的作用是什么", "化学", "技术直答",
     ["备用能源", "保温"], "通识拓展102"),
    ("QB-543", "发芽土豆为什么不能吃", "生活常识", "技术直答",
     ["龙葵素", "中毒"], "通识拓展102"),
    ("QB-544", "中国的糖料作物是什么", "地理学", "技术直答",
     ["甘蔗", "甜菜"], "通识拓展102"),
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
                               "level:L2", "status:verified", "batch:通识拓展102"],
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
    bank["version"] = "v1.94"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
