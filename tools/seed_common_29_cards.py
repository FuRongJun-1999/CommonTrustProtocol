# -*- coding: utf-8 -*-
"""seed_common_29_cards.py · 通识拓展批次29知识卡+题库（幂等）

29：天文学-航天服/生活常识-闪电与雷声/历史-郑成功收复台湾/生物学-保护色与拟态
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_spacesuit",
     "航天服的作用",
     "基础科学知识点内容（人话接口）", "天文学",
     "太空是真空环境，航天服就是穿在身上的「微型飞船」：①提供氧气、排走二氧"
     "化碳（太空没有空气，无法呼吸）；②维持稳定气压（真空中体液会沸腾——血压"
     "与外界压差会致命）；③保温与隔热（向阳面可超 100℃、背阳面可低至 -100℃，"
     "还有强辐射与微流星体防护）。舱外航天服重达 100 多公斤（但太空中失重搬"
     "运不费力）、造价数千万美元；出舱活动（EVA）前要吸纯氧排氮，防止关节中"
     "溶解的氮气形成气泡（减压病）。宇航员在太空说话靠无线电——真空不能传声。",
     ["宇航员在太空为什么要穿航天服", "航天服有什么作用", "太空是真空吗",
      "真空中为什么不能传声", "什么是减压病", "舱外航天服有多重"],
     ["问空间站生命维持系统", "问航天员选拔标准"],
     "atomic", "",
     "航天服=微型飞船：供氧+稳压(真空体液沸腾)+隔热防辐射；舱外服100+kg；出舱前吸氧排氮防减压病；真空不传声靠无线电。"),
    ("kp_card_lightning",
     "先见闪电后闻雷声",
     "基础科学知识点内容（人话接口）", "生活常识",
     "闪电和雷声是同一次放电的两种表现，我们总是先看到闪电、后听到雷声，因为"
     "光速远大于声速：光速约 30 万公里/秒（几乎瞬间到达），声速在空气中只有约 "
     "340 米/秒——闪电与雷声同时发出，光先到。用这个差可以估算距离：看到闪电"
     "后数秒数，每 3 秒约 1 公里（声音 3 秒走约 1 公里）。防雷常识：雷雨天不在"
     "大树下/空旷高地停留，关好门窗、不洗淋浴；「闪电高塔效应」使高耸孤立物更"
     "易被击中。",
     ["为什么先看到闪电后听到雷声", "光速和声速哪个快", "怎么估算雷区距离",
      "雷雨天为什么不能躲在大树下", "声速是多少", "打雷是怎么产生的"],
     ["问避雷针原理", "问雷暴天气形成"],
     "atomic", "",
     "先见闪电=光速(30万km/s)>>声速(340m/s)；数秒估距=3秒约1公里；防雷=避大树/高地/淋浴。"),
    ("kp_card_zhengchenggong",
     "郑成功收复台湾",
     "人文通识知识点内容（人话接口）", "历史",
     "1661-1662 年，民族英雄郑成功率军渡海东征，从荷兰殖民者手中收复台湾——"
     "明末 1624 年起荷兰人占据台湾南部 38 年，郑成功率约 2.5 万将士、数百艘战"
     "船从金门出发，经鹿耳门登陆，围困热兰遮城九个月，1662 年荷兰总督揆一投降"
     "签字。郑成功在台湾设府建制、屯田垦荒、传播中华文化，被台湾民众尊为「开"
     "台圣王」。台南市的开山王庙（延平郡王祠）即为纪念他；「国姓爷」是他的俗称"
     "（赐姓朱）。",
     ["收复台湾的民族英雄是谁", "郑成功是什么时候收复台湾的", "台湾曾被哪个国家占据",
      "热兰遮城在哪里", "开台圣王指谁", "国姓爷是谁"],
     ["问明清海防对比", "问台湾开发史"],
     "atomic", "",
     "郑成功 1661-1662 从荷兰殖民者(占台38年)手中收复台湾：金门出发·鹿耳门登陆·困热兰遮九个月；尊称开台圣王/国姓爷。"),
    ("kp_card_camouflage",
     "保护色与拟态",
     "基础科学知识点内容（人话接口）", "生物学",
     "动物的生存智慧——保护色：体色与环境相近以便隐藏自己或接近猎物（北极熊白"
     "毛/雪地、草蛐蛐绿身/草丛、比目鱼贴底变色）；拟态：外形或行为模仿其他物体"
     "（枯叶蝶像枯叶、竹节虫像树枝、无毒的王蛇模仿有毒珊瑚蛇的环纹）。变色龙的"
     "变色主要为了调节体温与传递信息，兼有隐蔽作用——皮肤里的色素细胞扩张收缩"
     "改变体色。警戒色是反向策略：鲜艳颜色警告天敌「我有毒/不好吃」（毒蘑菇斑"
     "蝰蛙黄黑纹蜜蜂）。三者都是自然选择长期塑造的适应。",
     ["变色龙为什么会变色", "什么是保护色", "枯叶蝶像枯叶是什么现象",
      "什么是拟态", "什么是警戒色", "北极熊为什么是白色的"],
     ["问动物行为学实验", "问生物分类演化树"],
     "atomic", "",
     "保护色=体色近似环境(北极熊/比目鱼)；拟态=形似他物(枯叶蝶/竹节虫)；警戒色=鲜艳示毒(蜜蜂)；变色龙主为调温与通讯。"),
]

QUESTIONS = [
    ("QB-249", "宇航员在太空为什么要穿航天服", "天文学", "技术直答",
     ["真空", "供氧", "气压"], "通识拓展29"),
    ("QB-250", "为什么先看到闪电后听到雷声", "物理学", "技术直答",
     ["光速", "声速"], "通识拓展29"),
    ("QB-251", "收复台湾的民族英雄是谁", "历史", "技术直答",
     ["郑成功"], "通识拓展29"),
    ("QB-252", "枯叶蝶像枯叶是什么现象", "生物学", "技术直答",
     ["拟态"], "通识拓展29"),
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
                               "level:L2", "status:verified", "batch:通识拓展29"],
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
    bank["version"] = "v1.21"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
