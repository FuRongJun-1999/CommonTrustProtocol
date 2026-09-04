# -*- coding: utf-8 -*-
"""seed_common_92_cards.py · 通识拓展批次92知识卡+题库（幂等）

92：物理学-能源与可持续发展/化学-分子和原子的本质区别/生物学-动物在生物圈中的作用/地理学-台湾省
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sustdev",
     "能源与可持续发展",
     "基础科学知识点内容（人话接口）", "物理学",
     "为什么要开发新能源：①化石能源有限且不可再生（按当前消耗速度煤约可采 100+"
     "年、石油约 50 年）；②化石燃烧排放 CO₂（温室效应）与污染物（酸雨/雾霾）。"
     "可持续能源路径：太阳能（光伏+光热）、风能（陆上+海上风电，中国装机世界第"
     "一）、水能（三峡/白鹤滩）、核能（裂变电站+未来聚变）、地热、潮汐、生物质"
     "能、氢能（最清洁，制储运技术攻关中）。节能同样重要：提高能源利用率=「第五"
     "能源」（单位 GDP 能耗下降）。中国「双碳」目标：2030 年前碳达峰、2060 年前"
     "碳中和——能源结构从化石为主转向非化石为主（2030 年非化石占比 25% 左"
     "右）。每人可行的节能：随手关灯、绿色出行、选购高能效电器。",
     ["为什么要开发新能源", "什么是碳达峰碳中和", "可持续发展的能源有哪些",
      "氢能为什么被称为终极能源", "中国新能源装机世界第一吗", "节约能源的意义"],
     ["问光伏产业链", "问能源转型路线图"],
     "atomic", "",
     "开发新能源因=化石有限+污染；路径=光风核水地热潮汐氢能；节能=第五能源；中国双碳=2030 碳达峰/2060 碳中和(非化石 25%+)；个人=节电绿色出行。"),
    ("kp_card_molatom",
     "分子和原子的本质区别",
     "基础科学知识点内容（人话接口）", "化学",
     "分子：保持物质化学性质的最小粒子（如水分子保持水的化学性质）；原子：化学"
     "变化中的**最小粒子**。本质区别：**在化学变化中，分子可以再分（分成原子），"
     "而原子不能再分**（原子只是重新组合）。以水电解为例：水分子分解为氢原子和氧"
     "原子（分子被分），氢原子两两结合成氢分子、氧原子结合成氧分子（原子重新组"
     "合）——原子种类和数目在化学反应前后都不变（质量守恒的微观解释）。分子与原"
     "子的共同点：质量体积都很小、不停运动、有间隔（热胀冷缩/三态变化/气体压缩"
     "的微观解释）。联系：分子由原子构成（分子≠一定比原子大——比较要在同类物质"
     "间）；由原子直接构成的物质（金属/稀有气体/金刚石）没有「分子」概念。",
     ["分子和原子的本质区别", "化学变化中分子和原子怎么变", "水分子分解成什么",
      "为什么反应前后质量不变", "分子和原子哪个大", "原子能直接构成物质吗"],
     ["问原子结构复习", "问化学方程式微观意义"],
     "atomic", "",
     "本质区别=化学变化中分子可分·原子不可分(只重组)：水电解=水分子→氢氧原子→氢/氧分子(原子种类数目不变=质量守恒微观解释)；共性=小微动隙；金属/稀有气体由原子直接构成。"),
    ("kp_card_animalrole",
     "动物在生物圈中的作用",
     "基础科学知识点内容（人话接口）", "生物学",
     "动物在生物圈中三大作用：①**维持生态平衡**——食物链食物网中的消费者，相互"
     "制约（草兔狐的动态平衡；消灭一种「害兽」可能引发连锁失衡——麻雀教训：1958"
     " 年除四害打麻雀致虫灾）；②**促进物质循环**——动物取食消化吸收、呼吸排出"
     " CO₂/排泄物，加速物质在生物与环境间的循环（分解者参与）；③**帮助植物传粉"
     "传播种子**——蜜蜂蝴蝶传粉（显花植物 80% 依赖动物传粉）、松鼠埋橡子（遗忘"
     "的成为新树）、苍耳挂动物皮毛、鸟吞果实排种远播。动物与人类关系：提供肉蛋奶"
     "皮毛、役用、观赏、仿生学灵感；也要防治有害动物（蝗灾/鼠害）——合理控制而"
     "非赶尽杀绝（生态位思维）。",
     ["动物在自然界中的作用", "为什么不能随意消灭一种动物",
      "动物如何促进物质循环", "蜜蜂对植物有什么作用", "除四害打麻雀的教训",
      "苍耳的种子靠什么传播"],
     ["问生态平衡自调节", "问传粉网络研究"],
     "atomic", "",
     "动物三作用=维持生态平衡(食物链制约·打麻雀致虫灾教训)+促进物质循环(消化呼吸排泄)+帮植物传粉播种(80% 显花植物靠动物)；害兽防治=合理控制非灭绝。"),
    ("kp_card_taiwan",
     "台湾省：祖国宝岛",
     "人文通识知识点内容（人话接口）", "地理学",
     "台湾省包括台湾岛（中国最大岛，约 3.6 万平方公里）、澎湖列岛、钓鱼岛等附属"
     "岛屿。地形：山地约占 2/3，纵贯南北的台湾山脉（玉山 3952 米为中国东部最高"
     "峰）；平原集中在西部。位置：北回归线穿过中南部——北部亚热带季风气候、南"
     "部热带季风气候；「米仓」「糖罐」「水果之乡」（香蕉菠萝荔枝）、「森林之海"
     "」（樟树世界之最，樟脑产量曾占世界 70%）。资源：矿产有限但水能（河流短急落"
     "差大——日月潭水电）、地热、渔业（黑潮暖流交汇）丰富。城市：台北（政治文化"
     "中心）、高雄（最大港口）。经济：20 世纪 60-90 年代「亚洲四小龙」之一，电子"
     "代工（半导体芯片制造——台积电全球领先）发达。与大陆关系：血脉相连（多为福"
     "建广东移民后裔，闽南语通行）、两岸同属一个中国。",
     ["台湾省包括哪些岛屿", "台湾的地形特点", "玉山的海拔",
      "台湾的物产有什么", "台积电是什么公司", "台湾岛的地形以什么为主"],
     ["问两岸经贸往来", "问台湾气候南北差异"],
     "atomic", "",
     "台湾省=台湾岛(最大岛·3.6 万km²·山地 2/3·玉山 3952m 东部最高)+澎湖钓鱼岛；北回归线穿过·物产丰富(樟脑曾 70%)；经济=电子代工(台积电)；闽南移民血脉相连。"),
]

QUESTIONS = [
    ("QB-501", "为什么要开发新能源", "物理学", "技术直答",
     ["枯竭", "污染"], "通识拓展92"),
    ("QB-502", "分子和原子的本质区别", "化学", "技术直答",
     ["化学变化", "可分", "不可分"], "通识拓展92"),
    ("QB-503", "动物在自然界中的作用", "生物学", "技术直答",
     ["生态平衡", "物质循环", "传粉"], "通识拓展92"),
    ("QB-504", "台湾的地形特点", "地理学", "技术直答",
     ["山地", "2/3"], "通识拓展92"),
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
                               "level:L2", "status:verified", "batch:通识拓展92"],
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
    bank["version"] = "v1.84"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
