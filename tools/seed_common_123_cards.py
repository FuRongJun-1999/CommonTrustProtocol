# -*- coding: utf-8 -*-
"""seed_common_123_cards.py · 通识拓展批次123知识卡+题库（幂等）

123：地理学-中国城市群/化学-燃气安全常识/生活常识-游泳安全
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_citygroup",
     "中国三大城市群",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国三大世界级城市群：①**京津冀城市群**——北京（政治文化科创）+天津（港"
     "口制造）+河北（产业承接地），功能互补：疏解非首都功能、雄安新区千年大计"
     "；②**长三角城市群**（沪苏浙皖）——中国经济体量最大：上海龙头+杭州数字经"
     "济+苏州制造业+合肥科创（量子信息），一体化国家战略；③**粤港澳大湾区**——"
     "9+2 城市（广州深圳香港澳门珠海等）：科技创新（深圳）+国际金融（香港）+制"
     "造业（东莞佛山）融合，跨制度合作典范。共同特点：都位于东部沿海平原、交通"
     "枢纽、人才集聚。世界对比：对标纽约湾区（金融）、旧金山湾区（科技）、东京"
     "湾区（产业）。",
     ["中国三大城市群", "京津冀协同发展战略", "粤港澳大湾区包括哪些城市",
      "长三角一体化", "雄安新区的作用", "世界著名湾区对比"],
     ["问湾区经济特征", "问城市群虹吸效应"],
     "atomic", "",
     "三大城市群=京津冀(首都功能疏解·雄安)+长三角(经济体量第一·沪杭苏合)+粤港澳(9+2·深港科创金融)；对标纽约旧金山东京湾区；共同点=沿海平原枢纽人才。"),
    ("kp_card_gassafety",
     "燃气安全常识",
     "生活常识知识点内容（人话接口）", "化学",
     "燃气泄漏应急处置「三要三不要」：**要**——立即开窗通风（稀释浓度）、关闭阀"
     "门（切断气源）、到室外拨打燃气公司电话报警；**不要**——不要开关任何电器"
     "（开关打火产生电火花）、不要在室内使用明火（打火机/火柴）、不要在现场拨打"
     "手机（电火花引爆）。燃气种类：天然气（甲烷，比空气轻往上飘）、液化石油气"
     "（比空气重沉聚地面）。气味来源：燃气本身无色无味，加入**四氢噻吩**警示剂"
     "（臭鸡蛋味）便于察觉泄漏。日常检查：肥皂水涂接口处看是否冒泡、燃气软管 18"
     " 个月更换、安装燃气报警器。一氧化碳中毒：燃气不完全燃烧产生（冬季紧闭门"
     "窗用燃气热水器是高危场景——CO 无色无味更危险）。",
     ["燃气泄漏怎么办", "燃气泄漏为什么不能开灯", "燃气报警器装哪里",
      "天然气和液化石油气的区别", "燃气为什么会有一氧化碳", "怎么检查燃气泄漏"],
     ["问燃气热水器安装规范", "问 CO 报警器与燃气报警器区别"],
     "atomic", "",
     "燃气泄漏三要=开窗+关阀+室外报警，三不=不开关电器不用明火不打手机（电火花引爆）；臭味=人为加四氢噻吩；软管 18 月换；CO=不完全燃烧·无色无味更险。"),
    ("kp_card_swimsafe",
     "游泳安全常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "游泳安全六不准（教育部防溺水）：不私自下水、不擅自与他人结伴、不在无家长"
     "教师带领下游泳、不到无安全设施无救援人员水域、不到不熟悉水域、不擅自下水"
     "施救。抽筋自救：小腿抽筋——仰漂、扳脚趾向身体方向拉伸；手指抽筋——握拳"
     "张开反复。遇人溺水：**智慧救援**——大声呼救+拨打 110/120+抛掷漂浮物（救"
     "生圈/空瓶/长杆），**不盲目下水**、不手拉手施救（连环溺亡主因）；下水救援"
     "须从背后接近（防被抱死）。岸上急救：清理口鼻异物→判断呼吸→无呼吸立即"
     " CPR（cprfirst 呼应）→有条件用 AED。野外水域危险：水下暗流/水草缠脚/淤"
     "泥/水温骤降抽筋——「野泳」是青少年溺水身亡的主要原因。",
     ["游泳抽筋怎么办", "遇到溺水者怎么办", "为什么不能盲目下水救人",
      "野泳有什么危险", "防溺水六不准", "游泳时腿抽筋怎么自救"],
     ["问溺水急救复习", "问救生器材使用"],
     "atomic", "",
     "防溺水六不准；抽筋自救=仰漂+扳脚趾拉伸；遇溺者=呼救+抛漂物+报警，勿盲目下水勿手拉手（连环溺亡主因）；下水从背后接近；岸上=清口鼻+CPR。"),
]

QUESTIONS = [
    ("QB-629", "中国三大城市群", "地理学", "技术直答",
     ["京津冀", "长三角", "粤港澳"], "通识拓展123"),
    ("QB-630", "燃气泄漏怎么办", "生活常识", "技术直答",
     ["开窗通风", "关阀门", "不能开灯"], "通识拓展123"),
    ("QB-631", "游泳抽筋怎么办", "生活常识", "技术直答",
     ["仰漂", "拉伸"], "通识拓展123"),
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
                               "level:L2", "status:verified", "batch:通识拓展123"],
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
    bank["version"] = "v3.7"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
