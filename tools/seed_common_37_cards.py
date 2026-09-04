# -*- coding: utf-8 -*-
"""seed_common_37_cards.py · 通识拓展批次37知识卡+题库（幂等）

37：化学-食盐成分/地理学-世界最大盆地/生物学-候鸟迁徙/历史-唐朝开国
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_salt",
     "食盐的成分与用途",
     "基础科学知识点内容（人话接口）", "化学",
     "食盐的主要成分是氯化钠（NaCl）：白色晶体、易溶于水、熔点约 801℃。来源主"
     "要有三：海盐（海水晒制）、湖盐/井盐、岩盐。加碘盐：为预防碘缺乏病（甲状"
     "腺肿大/大脖子病、克汀病），我国普遍在食盐中添加碘酸钾。生理作用：氯离子"
     "是胃酸（盐酸）的原料、钠离子维持体液平衡与神经传导——但过量摄入增加高血"
     "压风险，世卫建议成人每日不超过 5 克。食盐水可简单检验鸡蛋新鲜度（新鲜蛋"
     "下沉）。工业上电解饱和食盐水制氯气/烧碱（氯碱工业）。",
     ["食盐的主要成分是什么", "加碘盐加的是什么", "大脖子病缺什么",
      "每天吃多少盐合适", "海盐和井盐的成分一样吗", "电解食盐水生成什么"],
     ["问盐的化工产业链", "问低钠盐原理"],
     "atomic", "",
     "食盐=NaCl(海盐/湖盐井盐/岩盐)；加碘盐=加碘酸钾防大脖子病；钠维体液氯造胃酸；日限5g；电解食盐水→氯气+烧碱。"),
    ("kp_card_congobasin",
     "世界盆地之最",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界最大的盆地是刚果盆地（非洲中西部，面积约 337 万平方公里）——刚果河"
     "流经其间，盆地内部是世界第二大热带雨林（仅次于亚马孙），被称为「地球的第二"
     "个肺」。中国最大的盆地是塔里木盆地（新疆南部，约 40 多万平方公里），盆地"
     "中心是我国最大的沙漠塔克拉玛干沙漠；准噶尔盆地（北疆）内有我国第二大沙漠"
     "古尔班通古特沙漠；柴达木盆地（青海）是海拔最高的盆地（约 2600-3000 米），"
     "矿产资源丰富被称为「聚宝盆」；四川盆地因紫色土壤又称「紫色盆地」，农业发"
     "达号称「天府之国」。",
     ["世界最大的盆地是哪个", "刚果盆地有多大", "中国最大的盆地",
      "聚宝盆指哪个盆地", "紫色盆地是哪个", "塔克拉玛干沙漠在哪个盆地"],
     ["问盆地成因分类", "问雨林生态细节"],
     "atomic", "",
     "最大盆地=刚果(337万km²·第二大雨林·地球第二肺)；中国最大=塔里木(塔克拉玛干)；最高=柴达木(聚宝盆)；四川=紫色盆地。"),
    ("kp_card_migration",
     "候鸟迁徙",
     "基础科学知识点内容（人话接口）", "生物学",
     "候鸟是随季节往返迁徙的鸟类：秋天大雁/燕子等向南方飞——北方气温下降、昆"
     "虫和食物减少，飞往温暖的南方过冬；春天再北返繁殖。迁徙靠什么导航：太阳/"
     "星星位置、地磁场感应（体内有磁性物质）、地标记忆等多重机制配合。著名纪录"
     "：北极燕鸥每年往返南北极之间约 7 万公里，是迁徙距离最远的鸟；大雁南飞排成"
     "「人」字形/一字形——前鸟翼尖产生的上升气流帮助后鸟省力（领飞轮换）。留鸟"
     "（麻雀/喜鹊）不迁徙，靠换厚羽+储存食物+减少活动过冬。",
     ["大雁秋天为什么要往南飞", "什么是候鸟", "鸟类迁徙靠什么认路",
      "迁徙最远的鸟是哪种", "大雁为什么排成人字形", "麻雀冬天为什么不南飞"],
     ["问迁徙的能量储备", "问气候变化对迁徙影响"],
     "atomic", "",
     "候鸟南飞=避寒+觅食（北冬食物少）；导航=日月星+地磁+地标；北极燕鸥≈7万km/年最远；人字形=借前鸟翼尖上升气流省力；麻雀=留鸟。"),
    ("kp_card_tangfound",
     "唐朝的建立",
     "人文通识知识点内容（人话接口）", "历史",
     "唐朝的开国皇帝是李渊（唐高祖）：隋末天下大乱，617 年时任太原留守的李渊起"
     "兵反隋，攻入长安；618 年隋炀帝在江都被杀后，李渊称帝建立唐朝，定都长安"
     "（今西安）。真正为唐朝统一立下大功的是他的次子李世民（后来发动玄武门之"
     "变登基，即唐太宗，「贞观之治」的开创者）。唐朝（618-907）共 289 年，是中"
     "国古代最鼎盛的王朝之一：先后有贞观之治、武则天（中国唯一女皇帝）、开元盛"
     "世；安史之乱（755-763）由盛转衰，907 年朱温篡唐灭亡。长安当时是世界最大"
     "的国际化都市之一。",
     ["唐朝的开国皇帝是谁", "李渊是在哪里起兵的", "唐朝是哪一年建立的",
      "贞观之治是哪个皇帝时期", "中国唯一的女皇帝是谁", "安史之乱后唐朝怎么样"],
     ["问玄武门之变细节", "问唐朝官制科举"],
     "atomic", "",
     "唐朝 618 年李渊(唐高祖)建：太原起兵·定都长安；李世民=玄武门之变→贞观之治；武则天=唯一女皇；755 安史之乱转衰·907 亡。"),
]

QUESTIONS = [
    ("QB-281", "食盐的主要成分是什么", "化学", "技术直答",
     ["氯化钠", "NaCl"], "通识拓展37"),
    ("QB-282", "世界最大的盆地是哪个", "地理学", "技术直答",
     ["刚果盆地"], "通识拓展37"),
    ("QB-283", "大雁秋天为什么要往南飞", "生物学", "技术直答",
     ["迁徙", "避寒", "食物"], "通识拓展37"),
    ("QB-284", "唐朝的开国皇帝是谁", "历史", "技术直答",
     ["李渊", "唐高祖"], "通识拓展37"),
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
                               "level:L2", "status:verified", "batch:通识拓展37"],
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
    bank["version"] = "v1.29"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
