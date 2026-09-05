# -*- coding: utf-8 -*-
"""seed_common_131_cards.py · 通识拓展批次131知识卡+题库（幂等）

131：物理学-力学综合应用/历史学-都江堰与古代水利工程/地理学-中国土地资源
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞（三 id 均无撞已验）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_force_syn",
     "力学综合应用：漂浮问题分析法",
     "基础科学知识点内容（人话接口）", "物理学",
     "力学综合问题的通用分析法——以「轮船从长江驶入东海」为例：第一步定状态："
     "船始终**漂浮**在水面；第二步列平衡：漂浮时浮力等于重力（F浮=G），船的重"
     "力没变，所以浮力**不变**；第三步比密度：海水密度大于江水，由 F浮=ρ液·g·"
     "V排 可知，ρ液变大则 V排（排开水的体积）**变小**——船身**上浮**一些，吃水"
     "线变浅。反过来从海入江则下沉一些。同一原理的应用：密度计漂浮在任何液体中"
     "浮力都等于自重，液体密度越大浸入越浅（刻度上小下大）；载重线（吃水线）标"
     "尺就是让船在不同密度海域安全装载。综合题三步诀：定状态→列平衡→比较变量。",
     ["轮船从长江驶入东海浮力怎么变", "漂浮条件是什么", "船身会上浮还是下沉",
      "密度计的原理", "吃水线是什么", "力学综合题怎么分析"],
     ["问浮力公式数值计算（用浮力卡）", "问船的排水量载重计算"],
     "atomic", "",
     "力学综合三步诀=定状态→列平衡→比变量；漂浮恒有 F浮=G：江入海浮力不变、液体密度变大 V排 变小→船身上浮吃水线变浅；密度计同理（密度大浸入浅，刻度上小下大）。"),
    ("kp_card_dujujiangyan",
     "都江堰与古代水利工程",
     "人文通识知识点内容（人话接口）", "历史学",
     "都江堰——**战国时期**（约公元前 256 年）秦国蜀郡太守**李冰**父子主持修建，"
     "位于四川岷江上，是全世界迄今年代最久、唯一留存、以无坝引水为特征的宏大水"
     "利工程。三大主体工程：①**鱼嘴**——分水堤，把岷江分成内江（灌溉）与外江"
     "（泄洪）；②**飞沙堰**——泄洪排沙（二八分沙：八成泥沙排入外江）；③**宝"
     "瓶口**——控制进水量的咽喉通道。功效：防洪+灌溉，使成都平原「水旱从人，"
     "不知饥馑」成为**天府之国**，运行 2200 多年至今仍在使用——「活的水利博物"
     "馆」，2000 年列入世界文化遗产。中国古代大工程对照：长城（军事防御）、京"
     "杭大运河（南北漕运）、坎儿井（新疆地下引水）。郑国渠（陕西）与都江堰、灵"
     "渠并称秦代三大水利工程。",
     ["都江堰是谁修建的", "李冰父子", "天府之国是怎么来的",
      "鱼嘴飞沙堰宝瓶口的作用", "中国古代大工程有哪些", "秦代三大水利工程"],
     ["问三峡工程（现代水利）", "问长城的修筑目的（用长城卡）"],
     "atomic", "",
     "都江堰=战国秦蜀郡太守李冰父子修（前256年·岷江·无坝引水）：鱼嘴分水（内江灌外江泄）+飞沙堰泄洪排沙+宝瓶口控流→成都平原成天府之国，运行 2200 年至今=世界文化遗产；对照：长城防御/大运河漕运/坎儿井引水。"),
    ("kp_card_land_res",
     "中国土地资源的特点与保护",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国土地资源四大特点：①**类型齐全**——耕地、林地、草地、建设用地等都有，"
     "有利于因地制宜全面发展农、林、牧、渔；②**人均不足**——土地总量居世界第三，"
     "但人均占有量约为世界平均水平的 1/3；③**比例构成不合理**——耕地、林地比重"
     "小（耕地约只占 13%），难利用土地（沙漠/戈壁/高寒荒漠）多，后备耕地资源不"
     "足；④**分布不均**——耕地集中在东部季风区的平原和盆地，草地集中在西部内"
     "陆高原山地（自东向西：耕地→林地→草地递变）。因此国家把「**十分珍惜、合理"
     "利用土地和切实保护耕地**」作为基本国策，坚守 **18 亿亩耕地红线**（保障粮"
     "食安全）。每年 6 月 25 日为全国土地日。",
     ["中国土地资源的特点", "为什么保护耕地是基本国策", "18亿亩耕地红线",
      "我国土地利用类型有哪些", "人均耕地少", "全国土地日是哪天"],
     ["问水资源特点（用水资源卡）", "问具体农作物分布"],
     "atomic", "",
     "中国土地资源=类型齐全+人均不足(约世界1/3)+耕地林地比重小难利用地多+分布不均(东部耕地/西部草地)；国策=珍惜合理利用土地切实保护耕地，18 亿亩红线保粮食安全，6 月 25 日全国土地日。"),
]

QUESTIONS = [
    ("QB-659", "轮船从长江驶入东海（海水密度更大），它受到的浮力怎么变化？船身会升高还是下沉一些？", "物理学", "技术直答",
     ["不变", "上浮", "浮力等于重力", "排水体积变小"], "通识拓展131"),
    ("QB-660", "都江堰是谁主持修建的？它使哪个平原成为了「天府之国」？", "历史学", "技术直答",
     ["李冰", "成都平原"], "通识拓展131"),
    ("QB-661", "我国把「十分珍惜、合理利用土地和切实保护耕地」作为基本国策，主要是因为我国土地资源有什么特点？", "地理学", "技术直答",
     ["人均", "不足", "耕地比重小", "后备"], "通识拓展131"),
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
                               "level:L2", "status:verified", "batch:通识拓展131"],
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
    bank["version"] = "v4.4"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
