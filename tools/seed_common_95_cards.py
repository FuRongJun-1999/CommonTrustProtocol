# -*- coding: utf-8 -*-
"""seed_common_95_cards.py · 通识拓展批次95知识卡+题库（幂等）

95：物理学-电阻的概念/化学-中和反应的应用/生物学-影响生物的环境因素/地理学-中国水资源
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_resist",
     "电阻：导体对电流的阻碍作用",
     "基础科学知识点内容（人话接口）", "物理学",
     "电阻（R）表示导体对电流的**阻碍作用**大小，单位欧姆（Ω）。关键认知：电阻"
     "是导体本身的性质——由**材料、长度、横截面积、温度**决定（长而细的电阻大、"
     "短而粗的小；金属温度升高电阻增大），**与是否接电压、电流大小无关**——R=U/I"
     " 只是计算式（测量式），不是决定式（「没有电流就没有电阻」是错的）。滑动变"
     "阻器：靠改变接入电路的电阻丝**长度**来改变电阻（保护电路+调节电流）。电阻"
     "率：材料特性——银最小（导电最好）、镍铬合金大（做电热丝）、绝缘体巨大。超"
     "导（supercond 呼应）：某些材料温度降到临界温度以下电阻突降为零。",
     ["电阻是导体对电流的阻碍作用", "电阻与电压电流有关吗", "决定电阻大小的因素",
      "滑动变阻器的原理", "R=U/I 是决定式吗", "什么材料电阻最大"],
     ["问欧姆定律综合", "问变阻器接法「一上一下」"],
     "atomic", "",
     "电阻=对电流的阻碍·本身性质：由材料/长度/横截面积/温度决定——与 U、I 无关(R=U/I 是测量式非决定式)；滑动变阻器=改变接入长度；超导=零电阻特例。"),
    ("kp_card_neutralapp",
     "中和反应的实际应用",
     "基础科学知识点内容（人话接口）", "化学",
     "中和反应（酸+碱→盐+水）的四大应用：①**改良酸性土壤**——撒熟石灰"
     "（Ca(OH)₂）中和土壤酸性（最经典的农业应用）；②**治疗胃酸过多**——服用含"
     "氢氧化铝（Al(OH)₃）的胃药（中和过量盐酸，温和不伤胃——不能用强碱烧碱）；③"
     "**处理工厂废水**——用熟石灰中和硫酸厂/印染厂的酸性废水（环保达标排放）；④"
     "**蚊虫叮咬涂肥皂水**——蚁酸（酸性）被碱中和止痒。判断中和反应发生：借助酸"
     "碱指示剂（酚酞：碱中红色，滴加酸红色褪去即中和完成——酸碱滴定的原理）。中"
     "和反应都是放热反应（acidbody/exotherm 呼应）。应用化学观：化学知识服务生"
     "产生活的典型范式。",
     ["中和反应在实际中的应用", "改良酸性土壤用什么", "胃酸过多吃什么药中和",
      "怎么判断中和反应发生了", "中和反应放热还是吸热", "蚊子叮咬涂什么止痒"],
     ["问酸碱滴定实验", "问中和反应方程式集"],
     "atomic", "",
     "中和应用四例=熟石灰改酸土+氢氧化铝治胃酸+石灰处理酸废水+肥皂水止痒(蚁酸)；判断发生=酚酞褪色(滴定原理)；中和皆放热；强碱治胃酸禁(烧碱伤人)。"),
    ("kp_card_ecofactors",
     "影响生物生活的环境因素",
     "基础科学知识点内容（人话接口）", "生物学",
     "环境中影响生物生活和分布的因素叫**生态因素**，分两类：①**非生物因素**——"
     "光（植物向光/动物昼夜行为）、温度（南北物种差异/候鸟迁徙/水果地域性）、水"
     "（沙漠植物骆驼刺根系超长/雨林茂密）、空气、土壤；②**生物因素**——影响某生"
     "物的其他生物：捕食（猫捉鼠）、竞争（水稻与杂草争水肥）、共生（豆科与根瘤"
     "菌互利）、寄生（蛔虫与人体）、合作（蚂蚁群居）。经典探究实验：光对鼠妇（潮"
     "虫）生活的影响——对照实验，唯一变量是光照。生物与环境相互影响：环境塑造"
     "生物（适应——保护色），生物也改变环境（蚯蚓松土/大树成荫/森林调节气候）。",
     ["影响生物生活的环境因素", "生态因素分哪两类", "什么是共生关系",
      "光对鼠妇影响的实验", "生物与环境相互影响", "竞争关系举例"],
     ["问探究实验设计规范", "问适应性与应激性区分"],
     "atomic", "",
     "生态因素=非生物(光温水气土)+生物(捕食/竞争/共生/寄生/合作)；经典探究=光对鼠妇影响(唯一变量对照)；生物与环境互相影响——适应(保护色)与改造(蚯蚓松土)。"),
    ("kp_card_waterrsrc",
     "中国水资源的特点",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国水资源特点：①总量丰富——约 2.8 万亿立方米（世界第六），但**人均不足**"
     "（约为世界平均 1/4，是全球 13 个人均水资源最贫乏的国家之一）；②**时空分布"
     "不均**——空间：南多北少、东多西少（「八成水在长江流域及以南，耕地却六成在"
     "北方」——水土资源匹配差）；时间：夏秋多、冬春少，年际变化大。对策：跨流域"
     "调水（南水北调——snwd 呼应）解决空间不均；修水库（三峡/小浪底——蓄丰补"
     "枯）解决时间不均；节约用水+防治水污染（农业滴灌喷灌、工业循环用水、生活节"
     "水器具）——「节水优先」方针。3 月 22 日世界水日、中国水周（3.22-28）。华北"
     "缺水最严重（人口密+耕地多+降水少+工农业耗水大+地下水超采形成漏斗区）。",
     ["中国水资源的特点", "中国水资源时空分布", "解决水资源分布不均的措施",
      "华北为什么缺水严重", "世界水日是哪一天", "节水措施有哪些"],
     ["问海水淡化与节水", "问地下水超采治理"],
     "atomic", "",
     "中国水=总量 2.8 万亿 m³ 世界第六·人均≈世界 1/4；时空不均=南多北少+夏秋多→对策=南水北调+水库蓄丰补枯+节水优先；华北最缺(人密地多水少超采)；3.22 世界水日。"),
]

QUESTIONS = [
    ("QB-513", "电阻是导体对电流的阻碍作用", "物理学", "技术直答",
     ["本身性质", "材料", "长度"], "通识拓展95"),
    ("QB-514", "中和反应在实际中的应用", "化学", "技术直答",
     ["改良土壤", "治胃酸", "处理废水"], "通识拓展95"),
    ("QB-515", "影响生物生活的环境因素", "生物学", "技术直答",
     ["非生物因素", "生物因素"], "通识拓展95"),
    ("QB-516", "中国水资源的特点", "地理学", "技术直答",
     ["总量丰富", "人均不足", "时空不均"], "通识拓展95"),
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
                               "level:L2", "status:verified", "batch:通识拓展95"],
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
    bank["version"] = "v1.87"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
