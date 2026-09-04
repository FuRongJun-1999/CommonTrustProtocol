# -*- coding: utf-8 -*-
"""seed_common_107_cards.py · 通识拓展批次107知识卡+题库（幂等）

107：物理学-海洋高技术/化学-激光的特性与应用/生物学-鸟类的生殖与发育/地理学-北京城市职能
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_seatech",
     "海洋高技术",
     "基础科学知识点内容（人话接口）", "物理学",
     "海洋高技术三大方向：①深海探测——蛟龙号载人潜水器（7000 米级）/奋斗者号"
     "（10909 米坐底马里亚纳海沟）；②海水淡化（反渗透膜法）与海洋牧场（人工鱼"
     "礁+增殖放流）；③海洋可再生能源——潮汐能/波浪能/海上风电/温差能。技术难"
     "点：深海高压（每下潜 10 米增加一个大气压）、腐蚀、通信（电磁波衰减用声"
     "呐）。海洋强国战略：勘探开发+生态保护并重。",
     ["海洋高技术有哪些", "奋斗者号下潜深度", "什么是海洋牧场",
      "深海通信怎么解决"],
     ["问可燃冰开采"],
     "atomic", "",
     "答：深海探测(奋斗者 10909m)+海水淡化+海洋牧场+海洋能；难点=高压腐蚀通信；蛟龙号 7000 米级。"),
    ("kp_card_laser",
     "激光的特性与应用",
     "基础科学知识点内容（人话接口）", "物理学",
     "激光（Laser）四大特性：①单色性好（频率单一——颜色极纯）；②方向性好（几"
     "乎平行不发散——激光测距地球月球误差厘米级）；③亮度高（能量高度集中——可"
     "切割钢板）；④相干性好。应用：光纤通信（激光在光纤中全反射传输——互联网骨"
     "干）、激光手术（近视矫正）、激光切割焊接、条码扫描、激光雷达（自动驾驶）。"
     "激光与普通光区别：普通光向四面八方散、含多种颜色；激光单一频率同相位。",
     ["激光有什么特性", "激光的应用有哪些", "激光测距的原理",
      "光纤通信用什么光", "激光手术矫正近视", "激光雷达是什么"],
     ["问全息投影原理"],
     "atomic", "",
     "答：单色性好+方向性好(测距)+亮度高(切割)+相干性好；应用=光纤通信/激光手术/激光雷达/条码扫描。"),
    ("kp_card_birdrepro",
     "鸟类的生殖与发育",
     "基础科学知识点内容（人话接口）", "生物学",
     "鸟类生殖发育特点：体内受精、卵生，有复杂的繁殖行为——求偶（孔雀开屏/鸣"
     "唱）、筑巢、产卵、孵卵、育雏。鸟卵结构：①卵壳+卵壳膜——保护；②卵白——"
     "保护和提供水分营养；③**卵黄——卵细胞的主要营养部分**；④**胚盘**——内有"
     "细胞核，胚胎发育的部位（受精后色深略大）；⑤气室——供胚胎呼吸。早成鸟"
     "（鸡鸭——出壳即有绒毛能随亲鸟觅食）与晚成鸟（麻雀鸽子——出壳裸眼需亲鸟喂"
     "养）。",
     ["鸟类的生殖发育特点", "鸟卵的结构", "胚胎发育的部位",
      "什么是早成鸟晚成鸟"],
     ["问鸟类迁徙与繁殖区"],
     "atomic", "",
     "答：体内受精卵生+筑巢孵卵育雏；卵黄=营养·胚盘=胚胎发育部位·气室呼吸；早成鸡鸭/晚成麻雀。"),
    ("kp_card_beijing",
     "北京：祖国的首都",
     "人文通识知识点内容（人话接口）", "地理学",
     "北京的城市职能：全国政治中心（中央政府所在地）、文化中心（高校科研院所云"
     "集——北大清华/故宫颐和园长城）、国际交往中心（外国使馆/国际组织）、科技创"
     "新中心（中关村）。位置：华北平原北部边缘，背靠燕山，毗邻天津与河北。气候："
     "温带季风气候（冬季寒冷干燥夏季高温多雨）。历史：3000 多年建城史、800 多年"
     "建都史（金元明清都城）；名胜：故宫/天坛/颐和园/八达岭长城/周口店（世界遗"
     "产）。城市发展：疏解非首都功能（雄安新区）、京津冀协同发展。",
     ["北京的城市职能是什么", "北京位于什么平原", "北京有哪些世界遗产",
      "北京是什么气候类型", "雄安新区的作用", "北京建都有多少年历史"],
     ["问四合院与胡同文化", "问京津冀协同细节"],
     "atomic", "",
     "答：职能=政治/文化/国际交往/科技创新四中心；华北平原北缘·温带季风；3000 年建城 800 年建都；故宫天坛长城等世遗。"),
]

QUESTIONS = [
    ("QB-561", "海洋高技术有哪些", "物理学", "技术直答",
     ["深海探测", "海水淡化"], "通识拓展107"),
    ("QB-562", "激光有什么特性", "物理学", "技术直答",
     ["单色性", "方向性", "亮度高"], "通识拓展107"),
    ("QB-563", "鸟类的生殖发育特点", "生物学", "技术直答",
     ["体内受精", "卵生"], "通识拓展107"),
    ("QB-564", "北京的城市职能是什么", "地理学", "技术直答",
     ["政治", "文化", "国际交往", "科技创新"], "通识拓展107"),
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
                               "level:L2", "status:verified", "batch:通识拓展107"],
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
    bank["version"] = "v1.99"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
