# -*- coding: utf-8 -*-
"""seed_common_110_cards.py · 通识拓展批次110知识卡+题库（幂等）

110：物理学-音色的应用/化学-钙与人体健康/生物学-动物的社会行为
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_timbreuse",
     "音色的应用：听声辨物",
     "基础科学知识点内容（人话接口）", "物理学",
     "音色由发声体的**材料、结构**决定——不同发声体即使音调响度相同，音色也不"
     "同（波形不同）。「闻其声知其人」就是靠音色识别。应用：①敲瓷碗听声辨裂纹"
     "（有裂纹音色变哑——挑碗/铁路工敲击车轮检查）；②西瓜拍听生熟（生瓜声音清"
     "脆频率高）；③医生用听诊器分辨心肺音（杂音提示病变）；④主人听出爱犬叫声"
     "异常。反用：仿声（口技模仿鸟兽）——改变自己发声结构模拟他者音色。电子合"
     "成器可模拟各种乐器音色，但细微差异仍难完全复制（音色是「声纹」——声纹识"
     "别技术用于刑侦）。",
     ["音色由什么决定", "敲碗听声辨裂纹", "怎么挑西瓜", "听诊器的原理",
      "什么是声纹识别", "闻其声知其人的原理"],
     ["问音调响度音色复习", "问乐器音色原理"],
     "atomic", "",
     "音色=材料+结构决定(波形不同)：敲碗辨裂纹/拍瓜辨生熟/听诊器辨心肺杂音/声纹识别——「闻其声知其人」；合成器难完全复刻。"),
    ("kp_card_cacalcium",
     "钙：人体最多的矿物质",
     "基础科学知识点内容（人话接口）", "化学",
     "钙是人体含量最多的金属元素（约占体重 1.5-2%，99% 储存在骨骼和牙齿中）。"
     "缺钙表现：幼儿——佝偻病（方颅/X型腿/O型腿）；青少年——生长疼、发育受"
     "阻；成人——骨质疏松（易骨折，腰背痛）、抽筋（血钙低肌肉兴奋性增高）。补"
     "钙三要素：①摄入——牛奶（吸收最好）/豆制品/深绿色蔬菜；②维生素 D 助吸收"
     "（晒太阳皮肤合成）；③运动刺激骨钙沉积（骨骼「用进废退」）。注意：补钙不"
     "是越多越好（过量致肾结石/血管钙化）；草酸（菠菜）影响钙吸收——菠菜先焯水"
     "去草酸再与豆腐同炒更科学。",
     ["钙对人体的作用", "缺钙会得什么病", "为什么晒太阳能补钙",
      "菠菜和豆腐能一起吃吗", "骨质疏松的原因", "补钙越多越好吗"],
     ["问维生素D代谢机制", "问不同年龄钙需求量"],
     "atomic", "",
     "钙=人体最多矿物质(99% 在骨牙)：幼儿佝偻/老人骨质疏松抽筋；补钙三件套=奶制品+维生素D(晒太阳)+运动；菠菜焯水去草酸；过量致肾结石。"),
    ("kp_card_socialbeh",
     "动物的社会行为",
     "基础科学知识点内容（人话接口）", "生物学",
     "社会行为（社群行为）：同种生物群体内**分工合作**、有明确等级组织的行为。"
     "特征：①群体内有分工（白蚁：蚁后产卵/工蚁觅食筑巢/兵蚁保卫）；②有等级"
     "（狒狒群「首领」优先享有食物配偶）；③有信息交流（蜜蜂舞蹈/黑长尾猴不同叫"
     "声表示不同天敌）。典型：蜜蜂蜂群（蜂王/雄蜂/工蜂——工蜂分工还随日龄变"
     "化）、蚂蚁、狼群（合作狩猎）、象群（母系社会，首领为年长雌象）。意义：群"
     "体协作大大提高生存和繁衍能力。人类的社会性合作更复杂（语言文字/制度文"
     "化）。 mammal 呼应：狮群/狼群/猴群等级靠实力与联盟维系。",
     ["什么是动物的社会行为", "社会行为的特征", "蜜蜂群体的分工",
      "狼群怎么狩猎", "动物群体有什么意义", "白蚁的分工"],
     ["问灵长类社会结构", "问通讯行为复习"],
     "atomic", "",
     "社会行为=群体分工合作+等级+信息交流：白蚁三型分工/蜂群工蜂日龄分工/狼群合作狩猎/象群母系；意义=提高生存繁衍力；人类合作更复杂(语言制度)。"),
]

QUESTIONS = [
    ("QB-577", "音色由什么决定", "物理学", "技术直答",
     ["材料", "结构"], "通识拓展110"),
    ("QB-578", "缺钙会得什么病", "化学", "技术直答",
     ["佝偻病", "骨质疏松"], "通识拓展110"),
    ("QB-579", "什么是动物的社会行为", "生物学", "技术直答",
     ["分工合作", "群体"], "通识拓展110"),
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
                               "level:L2", "status:verified", "batch:通识拓展110"],
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
    bank["version"] = "v2.2"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
