# -*- coding: utf-8 -*-
"""seed_common_48_cards.py · 通识拓展批次48知识卡+题库（幂等）

48：物理学-功与功率/化学-石墨与金刚石/生物学-乳酸菌与酸奶/历史-武则天
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_power",
     "功与功率",
     "基础科学知识点内容（人话接口）", "物理学",
     "功（W）=力×物体在力的方向上移动的距离（W=Fs，单位焦耳 J）——两个必要因"
     "素：有力、沿力方向移动距离（提水桶水平走，对水桶不做功；推墙不动也不做"
     "功）。功率（P）=单位时间完成的功（P=W/t，单位瓦特 W）——表示做功**快慢**"
     "的物理量，不是做功多少。例：同样把 100 斤米搬上楼，慢搬快搬做的功一样，"
     "但功率不同（快者功率大）。常见功率：人短跑可达数百瓦、家用空调约 1000 瓦"
     "（1 千瓦）、一辆轿车约 100 千瓦。1 马力≈735 瓦。机械效率=有用功/总功（永"
     "远小于 100%，因摩擦等额外功不可避免）。",
     ["功率是表示什么的物理量", "功的计算公式", "什么情况不做功",
      "功率和功的区别", "1马力等于多少瓦", "什么是机械效率"],
     ["问动能势能转化计算", "问电功率千瓦时"],
     "atomic", "",
     "功 W=Fs(有力+沿力方向移距才做功)；功率 P=W/t 表示做功快慢(瓦特)；同功不同时→功率不同；机械效率=有用功/总功<100%。"),
    ("kp_card_allotrope",
     "石墨与金刚石：同素异形体",
     "基础科学知识点内容（人话接口）", "化学",
     "石墨和金刚石都由碳元素（C）组成，性质却天差地别——金刚石最硬（莫氏硬度 "
     "10，切玻璃/钻头）、璀璨透明；石墨质软（铅笔芯）、深灰、能导电（做电极）。"
     "差别全在**原子排列**：金刚石是立体网状结构（每个碳连 4 个碳，坚固无比）；"
     "石墨是层状结构（层内六边形网、层间易滑动所以软、且有自由电子所以导电）。"
     "这样的「同素异形体」还有：氧气 O₂ 与臭氧 O₃、红磷与白磷。碳家族新成员石"
     "墨烯（单层石墨，2004 年发现）：只有一个原子厚、导电导热超强、最薄最硬的"
     "新材料（2010 年诺贝尔奖）。铅笔芯=石墨+黏土，不是铅（「铅笔」是历史误名）。"
     "人造金刚石：高温高压把石墨「压」成金刚石。",
     ["铅笔芯是金属吗", "石墨和金刚石有什么区别", "什么是同素异形体",
      "金刚石为什么最硬", "石墨为什么能导电", "什么是石墨烯"],
     ["问碳纳米管 fullerene", "问人造钻石工艺"],
     "atomic", "",
     "石墨与金刚石=同为碳·原子排列不同（立体网状 vs 层状）故最硬 vs 软导电；同素异形体=O₂/O₃；铅笔芯=石墨+黏土非铅；石墨烯=诺奖新材料。"),
    ("kp_card_lactobacillus",
     "乳酸菌与酸奶",
     "基础科学知识点内容（人话接口）", "生物学",
     "酸奶是牛奶被乳酸菌发酵的产物：乳酸菌把乳糖发酵成乳酸——蛋白质遇酸凝固形"
     "成凝冻状（酸奶比牛奶「稠」的原因），酸味即来自乳酸。乳酸菌是**益生菌**："
     "抑制肠道有害菌、帮助消化（部分人群乳糖不耐受——喝牛奶拉肚子，喝酸奶没事，"
     "因为乳糖已被分解）。发酵条件：乳酸菌是厌氧菌（不需要氧气），适宜温度约 40"
     "℃——自制酸奶把牛奶+菌种保温 6-8 小时即可。同门发酵食品：泡菜（乳酸菌，"
     "无氧腌制）、酸菜、奶酪。保存注意：酸奶不能加热（杀死菌+蛋白质变性口感差）；"
     "「益生菌」产品活菌数才是关键（常温酸奶经巴氏杀菌无活菌，但营养仍在）。",
     ["酸奶里的乳酸菌有什么用", "牛奶为什么变成酸奶", "乳糖不耐受是什么",
      "自制酸奶要什么温度", "泡菜发酵靠什么菌", "常温酸奶还有活菌吗"],
     ["问肠道菌群研究", "问发酵食品大全"],
     "atomic", "",
     "酸奶=乳酸菌发酵：乳糖→乳酸→蛋白凝固(稠)+酸味；益生菌=抑害菌助消化；乳糖不耐者宜酸奶(乳糖已分解)；厌氧·约40℃·6-8h；泡菜同门。"),
    ("kp_card_wuzetian",
     "武则天：唯一的女皇帝",
     "人文通识知识点内容（人话接口）", "历史",
     "武则天（624-705）是中国历史上唯一被正史承认的女皇帝：唐太宗时入宫为才人，"
     "太宗死后入感业寺为尼，被高宗召回封昭仪、立为皇后（废王立武），与高宗并称"
     "「二圣」；高宗死后先后废黜中宗、睿宗两个儿子，690 年称帝，改国号为**周**"
     "（史称武周）——时年 67 岁，是中国即位年龄最大的皇帝之一。治国评价：承贞观"
     "之启开元——重用酷吏打击门阀贵族，也首创殿试与武举广纳人才（狄仁杰、姚崇"
     "皆其提拔）；晚年立李显为太子恢复李唐。705 年神龙政变被迫退位，同年病逝，"
     "遗诏去帝号、立**无字碑**（功过留待后人评说的解读流传最广）。设「十二年一"
     "次」的女皇专有年号「天册万岁」等皆其创举。",
     ["中国历史上唯一的女皇帝是谁", "武则天改国号为什么", "无字碑在哪里",
      "殿试和武举是谁首创的", "神龙政变", "武则天的治国评价"],
     ["问太平公主上官婉儿", "问唐代女性地位"],
     "atomic", "",
     "武则天=唯一女皇帝：太宗才人→高宗皇后(二圣)→690 称帝改国号周；承贞观启开元（酷吏+殿试武举纳贤·狄仁杰姚崇）；705 神龙政变退位·无字碑。"),
]

QUESTIONS = [
    ("QB-325", "功率是表示什么的物理量", "物理学", "技术直答",
     ["做功快慢"], "通识拓展48"),
    ("QB-326", "铅笔芯是金属吗", "化学", "技术直答",
     ["石墨", "碳", "不是"], "通识拓展48"),
    ("QB-327", "酸奶里的乳酸菌有什么用", "生物学", "技术直答",
     ["发酵", "益生菌"], "通识拓展48"),
    ("QB-328", "中国历史上唯一的女皇帝是谁", "历史", "技术直答",
     ["武则天"], "通识拓展48"),
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
                               "level:L2", "status:verified", "batch:通识拓展48"],
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
    bank["version"] = "v1.40"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
