# -*- coding: utf-8 -*-
"""seed_common_124_cards.py · 通识拓展批次124知识卡+题库（幂等）

124：物理学-家电安全使用综合/生活常识-辨识过期食品/化学-常见甜味剂
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_apphysafe",
     "家电安全使用综合指南",
     "基础科学知识点内容（人话接口）", "物理学",
     "家电安全使用要点：①**防过载**——插板同时插多个大功率电器（空调+电暖器+"
     "电磁炉）→干路电流过大→导线过热起火；②**防漏电**——湿手不碰开关插头、"
     "浴室用防溅插座、大功率电器接三孔插座（地线导走漏电）；③**防老化**——电"
     "线绝缘层老化开裂及时更换、电器超期服役（冰箱 10-15 年）；④**雷雨天**——"
     "拔掉电视/电脑电源（雷电波沿电网侵入）；⑤**长期不用**——拔掉插头（待机耗"
     "电+老化隐患）；⑥**灭火**——电器着火先断电，不能直接用水泼（残留电荷+水"
     "导电），用干粉灭火器。三孔插座的地线：连接电器金属外壳——漏电时电流走地"
     "线而非人体。",
     ["家电安全使用注意事项", "插板上为什么不能插多个大功率电器",
      "湿手为什么不能碰开关", "电器着火怎么办", "三孔插座的地线作用",
      "雷雨天要拔电源吗"],
     ["问漏电保护器原理", "问电器使用寿命表"],
     "atomic", "",
     "家电安全=防过载(插板限大功率)+防漏电(湿手勿触·三孔地线)+防老化(超期更换)+雷雨拔电源+电器着火先断电禁水泼·用干粉。"),
    ("kp_card_expiredfood",
     "辨识变质食品",
     "生活常识知识点内容（人话接口）", "生活常识",
     "辨识食品变质的「一看二闻三触」：①**看**——变色（肉发绿/米发黄有霉斑/罐"
     "头胀罐）、发黏（表面黏液=细菌大量繁殖）、霉斑（绿/黑/白毛——霉菌菌落）；"
     "②**闻**——酸腐味/哈喇味（油脂酸败）/霉味/氨味；③**触**——发黏发软（肉"
     "类）、弹性消失（按压不回弹）。高危食品：散装熟食/隔夜卤味/生腌海鲜/切开的"
     "西瓜（冷藏超 24 小时风险大）。李斯特菌：可在冰箱低温繁殖（「冰箱杀手」—"
     "—孕妇感染致流产），剩菜冷藏也须彻底加热再吃。误食变质食品：立即停止食"
     "用、催吐（意识清醒时）、多饮水、症状严重（呕血/高热/脱水）立即就医并保留"
     "剩余食物样本。",
     ["怎么判断食品变质", "食品变质的迹象", "罐头胀罐能吃吗",
      "剩菜要彻底加热吗", "什么是李斯特菌", "误食变质食品怎么办"],
     ["问食源性疾病类型", "问冰箱储存分区"],
     "atomic", "",
     "变质辨识=一看(变色霉斑胀罐)二闻(酸腐哈喇)三触(发黏无弹性)；李斯特菌冰箱繁殖——剩菜彻底加热；误食=停食催吐就医留样；罐头胀罐=产气变质勿食。"),
    ("kp_card_sweeteners",
     "常见甜味剂",
     "基础科学知识点内容（人话接口）", "化学",
     "甜味剂分两类：①**营养性甜味剂**（有热量）——蔗糖、果糖、葡萄糖、麦芽糖"
     "浆（过量致肥胖/龋齿/血糖问题）；②**非营养性甜味剂**（代糖，几乎零热"
     "量）：**糖精**（最古老，19 世纪发现，曾因「致癌」谣言被误解——后证清"
     "白）、**阿斯巴甜**（可乐无糖款，苯丙酮尿症患者禁用——含苯丙氨酸）、**三"
     "氯蔗糖**（蔗糖素，稳定性好可烘焙）、**赤藓糖醇**（天然糖醇，耐受性好但过"
     "量腹泻）。WHO 2023 建议：不要用非糖甜味剂控制体重（长期效果不明且可能有"
     "代谢风险）——「无糖≠可以无限喝」。天然代糖：甜菊糖苷（甜叶菊提取，天"
     "然零卡）、罗汉果甜苷。",
     ["常见甜味剂有哪些", "阿斯巴甜安全吗", "赤藓糖醇是什么",
      "无糖饮料真的无糖吗", "甜味剂有害吗", "什么是代糖"],
     ["问甜味剂研究进展", "问糖与代谢健康"],
     "atomic", "",
     "甜味剂两类=营养性(蔗糖果糖·有热量)vs 非营养(糖精/阿斯巴甜(苯丙酮尿禁)/三氯蔗糖/赤藓糖醇/甜菊糖苷·零卡)；WHO：代糖非长期控重方案——无糖≠无限喝。"),
]

QUESTIONS = [
    ("QB-632", "家电安全使用注意事项", "物理学", "技术直答",
     ["过载", "湿手", "地线"], "通识拓展124"),
    ("QB-633", "怎么判断食品变质", "生活常识", "技术直答",
     ["变色", "异味", "霉斑"], "通识拓展124"),
    ("QB-634", "常见甜味剂有哪些", "化学", "技术直答",
     ["糖精", "阿斯巴甜", "赤藓糖醇"], "通识拓展124"),
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
                               "level:L2", "status:verified", "batch:通识拓展124"],
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
    bank["version"] = "v3.8"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
