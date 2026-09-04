# -*- coding: utf-8 -*-
"""seed_common_77_cards.py · 通识拓展批次77知识卡+题库（幂等）

77：物理学-半导体/化学-化合价/生物学-传染病的预防/地理学-大陆漂移
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_semicond",
     "半导体：导电性可控制的材料",
     "基础科学知识点内容（人话接口）", "物理学",
     "半导体（硅/锗/砷化镓等）导电能力介于导体与绝缘体之间，最大特点是**可控**："
     "①掺杂微量杂质（硼→P 型/磷→N 型）改变导电性；②温度、光照、电压都能改变"
     "其导电性——热敏电阻（测温）、光敏电阻（路灯自动开关）、压敏元件。二极管="
     "单向导电（正向通反向断——整流、LED 发光）；三极管/ MOSFET=电子开关与放"
     "大——亿万只集成起来就是芯片（siliconchip 呼应）。发明脉络：1947 年贝尔实"
     "验室发明晶体管（巴丁/布拉顿/肖克莱获诺奖），取代电子管开启信息时代。太阳"
     "能电池=光生伏特效应的半导体器件。日常鉴别：金属温度升高电阻增大，半导体温"
     "度升高电阻反而减小（负温度系数）。",
     ["二极管三极管是什么材料", "什么是半导体", "半导体的导电性怎么控制",
      "二极管的作用是什么", "晶体管是谁发明的", "热敏电阻的原理"],
     ["问 PN 结物理", "问集成电路制程"],
     "atomic", "",
     "半导体(Si/Ge)=导电介于导绝之间且可控：掺杂(硼 P 型/磷 N 型)/温光压改变导电；二极管单向导电(整流/LED)·三极管=开关放大；1947 贝尔晶体管→信息时代。"),
    ("kp_card_valence",
     "化合价：写化学式的规则",
     "基础科学知识点内容（人话接口）", "化学",
     "化合价是原子相互化合时的「价数」规则：①氧通常 -2 价、氢通常 +1 价；②金"
     "属通常显正价、非金属显负价；③化合物中正负化合价**代数和为零**——这就是水"
     "写作 H₂O（+1×2 + (-2) = 0）而不是 HO 的原因。常见价态：钠 +1、钙 +2、铝"
     " +3；氯在 HCl 中 -1；碳有 +2/+4 等。单质中元素化合价为 0。口诀「一价钾钠"
     "氯氢银，二价氧钙钡镁锌，三铝四硅五价磷」；「十字交叉法」写化学式：铝 +3 与"
     "氧 -2 → Al₂O₃。化合价与离子电荷同源——原子得失电子后带电成离子（钠失一"
     "个电子=Na⁺=+1 价）。",
     ["水的化学式为什么是H₂O", "什么是化合价", "化合价口诀",
      "十字交叉法怎么写化学式", "单质的化合价是多少", "化合价和离子的关系"],
     ["问常见原子团价态", "问化学式书写练习"],
     "atomic", "",
     "化合价规则：氢+1/氧-2/金属正非金属负/化合物代数和=0(故 H₂O 非 HO)；单质=0；口诀一价钾钠氯氢银…；十字交叉写式 Al₂O₃；价态=得失电子数。"),
    ("kp_card_epidemic",
     "传染病的预防三环节",
     "基础科学知识点内容（人话接口）", "生物学",
     "传染病流行的三个基本环节：①**传染源**（能散播病原体的人或动物——患者/携"
     "带者/病媒动物）；②**传播途径**（空气/飞沫、饮食、接触、虫媒等）；③**易感"
     "人群**（对病原体缺乏免疫力的人）。预防措施对应三环节：控制传染源（隔离治"
     "疗患者、捕杀处理病畜）、切断传播途径（消毒/通风/戴口罩/洗手/灭蚊）、保护"
     "易感人群（接种疫苗/锻炼提高免疫力）——新冠防疫的「隔离+口罩消毒+疫苗」正"
     "是三管齐下。传染病分类：甲类（鼠疫/霍乱——强制管理）、乙类（新冠/乙肝/艾"
     "滋等——严格管理）、丙类（监测管理）。抗原 vs 抗体：疫苗（抗原）刺激人体自"
     "产抗体——与直接注射抗体（如破伤风抗毒素）机理不同。",
     ["传染病的预防措施", "传染病流行的三个环节", "什么是易感人群",
      "接种疫苗属于哪一环节", "甲类传染病有哪些", "抗原和抗体的区别"],
     ["问疫苗分类复习", "问流行病学调查"],
     "atomic", "",
     "三环节=传染源/传播途径/易感人群→对策=控制传染源(隔离)+切断途径(消毒口罩洗手灭蚊)+保护易感(疫苗锻炼)；甲类=鼠疫霍乱；疫苗是抗原诱生抗体。"),
    ("kp_card_wegener",
     "大陆漂移与板块构造",
     "人文通识知识点内容（人话接口）", "地理学",
     "1912 年德国气象学家**魏格纳**提出大陆漂移学说：病床上看世界地图发现大西洋"
     "两岸轮廓吻合（南美东岸与非洲西岸像拼图），且两岸古生物化石/地层/山脉相吻"
     "合——推测约 2-3 亿年前所有大陆连成一块「泛大陆」（盘古大陆），后来逐渐分"
     "离漂移。当时因无法解释漂移动力被冷落；1960 年代海底扩张说+板块构造理论问"
     "世（岩石圈分为六大板块，漂浮在软流层上缓慢移动，年移速几厘米——「指甲生"
     "长速度」），魏格纳获得平反。板块内部稳定、交界处活跃——全球两大火山地震"
     "带：环太平洋带、地中海-喜马拉雅带（日本/中国西南多震的原因）。证据链：大"
     "陆轮廓/古化石（中龙/舌羊齿）/岩层连续性/古气候（南极煤层=曾在温带）。",
     ["大陆漂移学说是谁提出的", "魏格纳怎么发现大陆漂移", "板块构造理论",
      "世界两大火山地震带", "泛大陆是什么", "板块交界处为什么多地震"],
     ["问珠峰仍在长高的机制", "问海底扩张证据"],
     "atomic", "",
     "魏格纳 1912 大陆漂移(地图轮廓+化石地层吻合·泛大陆分离)——动力困感遭冷落→60 年代板块构造平反：六板块漂于软流层·年移几厘米；交界活跃=环太平洋/地中海喜马拉雅两带。"),
]

QUESTIONS = [
    ("QB-441", "二极管三极管是什么材料", "物理学", "技术直答",
     ["半导体"], "通识拓展77"),
    ("QB-442", "水的化学式为什么是H₂O", "化学", "技术直答",
     ["化合价"], "通识拓展77"),
    ("QB-443", "传染病的预防措施", "生物学", "技术直答",
     ["控制传染源", "切断传播途径", "保护易感人群"], "通识拓展77"),
    ("QB-444", "大陆漂移学说是谁提出的", "地理学", "技术直答",
     ["魏格纳"], "通识拓展77"),
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
                               "level:L2", "status:verified", "batch:通识拓展77"],
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
    bank["version"] = "v1.69"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
