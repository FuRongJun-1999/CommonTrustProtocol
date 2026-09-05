# -*- coding: utf-8 -*-
"""seed_common_152_cards.py · 通识拓展批次152知识卡+题库（幂等·两卡精批次）

152：生活常识-方便面辟谣与改良吃法/生活常识-低头族与颈椎健康
KCCS 四要素+题干原句触发词。三重预检：方便面双库零覆盖；颈椎与 bones206
骨骼结构卡划界（现代病预防角度）；清明上河图/火山/水垢等候选命中已有覆盖弃。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_instantnoodle",
     "方便面的真相与改良吃法",
     "生活常识知识点内容（人话接口）", "生活常识",
     "辟谣与真相：①「防腐剂多所以坏不了」——**大多误解**：面饼经油炸或热风干"
     "燥脱水（水分活度极低微生物难繁殖）+密封包装，本身就能长期保存，很多面饼"
     "**不加或少加防腐剂**；酱包因高盐高油也不易腐坏；②**真正的问题**=营养结"
     "构：高钠（一包连汤下肚钠≈全天推荐上限）、精制碳水为主、缺优质蛋白/膳食"
     "纤维/维生素；③**改良吃法**——加鸡蛋+青菜/番茄补蛋白维生素、料包粉包只"
     "放一半减盐、**汤少喝或不喝**（钠大本营）、选非油炸面饼（脂肪减半）；④定"
     "位：应急方便食品偶尔吃无妨，别当主餐长期吃——「吃泡面致死」类谣言无科"
     "学依据，均衡饮食才是关键。",
     ["方便面防腐剂多吗", "吃泡面对身体不好吗", "方便面怎么吃更健康",
      "非油炸面饼", "泡面汤能喝吗", "方便面营养"],
     ["问食品添加剂（用食品安全卡）", "问外卖健康（用外卖卡）"],
     "atomic", "",
     "方便面辟谣=脱水+密封本身防腐、面饼多不加防腐剂；真问题=高钠(一包≈全天上限)+营养单一缺蛋白纤维；改良=加蛋青菜+料包减半+汤少喝+选非油炸；偶尔应急无妨勿当主餐，均衡饮食是关键。"),
    ("kp_card_textneck",
     "低头族与颈椎健康",
     "生活常识知识点内容（人话接口）", "生活常识",
     "低头角度与颈椎负荷（头约 5kg，低头越狠负担越大）：平视≈5kg；**低头 15°"
     "≈12kg、30°≈18kg、60°≈27kg**——相当于脖子挂着个七八岁孩子。长期低头=颈"
     "椎**生理曲度变直甚至反弓**、椎间盘受压退变、颈肩肌劳损，出现酸痛/僵硬/"
     "手麻/头晕（颈椎病年轻化——门诊常见十几岁初患者）。预防：①屏幕抬到**平"
     "视**高度（手机举到眼睛水平、电脑垫高显示器）；②每低头 **20-30 分钟**起"
     "身活动（20-20-20 法则护眼同理）；③温和锻炼——「米字操」缓慢写米字、耸"
     "肩扩胸、游泳（蛙泳抬头）放风筝；④枕头一拳高支撑颈曲（别高枕无忧——高"
     "枕=整夜低头）；⑤**警示**：持续手麻/放射性疼痛/行走踩棉感尽早就医，勿"
     "大力转脖子「咔咔」掰响（有风险）。",
     ["低头玩手机颈椎承受多少", "颈椎病怎么预防", "米字操",
      "高枕真的无忧吗", "手机看多了脖子疼怎么办", "颈椎生理曲度变直"],
     ["问颈椎病治疗（就医）", "问腰椎保护"],
     "atomic", "",
     "低头负荷=平视 5kg/15° 12kg/30° 18kg/60° 27kg；长期低头致曲度变直椎间盘退变（颈肩痛手麻年轻化）；预防=屏幕平视+20-30 分钟活动+米字操游泳+枕头一拳高；持续手麻踩棉感尽早就医勿暴力掰颈。"),
]

QUESTIONS = [
    ("QB-714", "方便面保质期长是因为防腐剂很多吗？怎么吃泡面更健康？", "生活常识", "技术直答",
     ["脱水", "误解", "高钠", "加蛋", "青菜", "料包", "非油炸"], "通识拓展152"),
    ("QB-715", "低头 60 度玩手机时颈椎承受的负荷大约是多少？怎么预防颈椎病？", "生活常识", "技术直答",
     ["27", "公斤", "kg", "平视", "米字操", "活动"], "通识拓展152"),
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
                               "level:L2", "status:verified", "batch:通识拓展152"],
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
    bank["version"] = "v4.25"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
