# -*- coding: utf-8 -*-
"""seed_common_67_cards.py · 通识拓展批次67知识卡+题库（幂等）

67：物理学-超重与失重/化学-硅与芯片/生物学-基因工程/地理学-梅雨与伏旱
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_weightless",
     "超重与失重",
     "基础科学知识点内容（人话接口）", "物理学",
     "体重（对支持物的压力）随加速度变化的两个现象：①超重——加速度向上（电梯"
     "上升启动/加速上升），人对地板压力变大（超重感「心悬起来」的反向：被压向"
     "地板）；②失重——加速度向下（电梯下降启动/游乐场俯冲），压力变小，**完全"
     "失重**=加速度等于重力加速度 g（自由落体/太空轨道飞行）。关键误区：太空"
     "宇航员漂浮不是因为「没有重力」（轨道高度重力仍有地面的约 90%）——而是飞"
     "船与宇航员一起自由下落（绕地球「下落」永远落不到地面），处于完全失重状"
     "态。失重生活：喝水要用吸管（水不往低处流）、睡觉要绑睡袋、汗珠不会滴落、"
     "骨钙流失（需锻炼对抗）。过山车俯冲/跳楼机=部分失重刺激感的来源。",
     ["宇航员在太空为什么漂浮", "什么是完全失重", "超重和失重怎么判断",
      "太空中还有重力吗", "电梯里为什么有心悬感", "失重对身体的危害"],
     ["问太空微重力实验", "问电梯超重失重计算"],
     "atomic", "",
     "超重=加速度向上(压力变大)/失重=加速度向下·完全失重=a=g(轨道飞行=持续自由下落)；宇航员漂浮≠无重力(仍有 90%)而是共同下落；失重=吸管喝水/骨钙流失。"),
    ("kp_card_siliconchip",
     "硅：从沙子到芯片",
     "基础科学知识点内容（人话接口）", "化学",
     "芯片（集成电路）的原料是最普通的元素——**硅**（从沙子/石英中的二氧化硅提"
     "炼）：提纯到 99.999999999%（11 个 9 的电子级多晶硅）→拉制成单晶硅棒→切"
     "成硅片（晶圆）→光刻/蚀刻/掺杂等数百道工序，在指甲盖大小的面积上集成上百"
     "亿个晶体管。硅是半导体：导电性介于导体与绝缘体之间，掺杂微量硼/磷可精确"
     "控制导电性——这是晶体管「开关」的基础。世界第一条：中国是全球最大芯片消费"
     "市场，制造正加速追赶（中芯国际等）；光刻机（荷兰 ASML 的 EUV）是卡脖子环"
     "节。硅的日用面：玻璃/水泥/陶瓷也含硅（硅酸盐），光纤=超纯石英玻璃。太阳能"
     "电池同样是硅片（光伏与芯片共享上游）。",
     ["芯片的原料是什么", "硅是导体还是绝缘体", "晶圆是什么",
      "芯片为什么难造", "光刻机是干什么用的", "沙子能变成芯片吗"],
     ["问光刻工艺流程", "问半导体掺杂原理"],
     "atomic", "",
     "芯片原料=硅(沙子/石英 SiO₂ 提纯至 11 个 9→单晶棒→晶圆→光刻蚀刻数百道)；半导体=掺杂控导电(晶体管开关)；光刻机=EUV 卡脖子；光伏芯片共享硅上游。"),
    ("kp_card_geneeng",
     "基因工程与转基因",
     "基础科学知识点内容（人话接口）", "生物学",
     "基因工程（基因拼接/重组 DNA 技术）：像「剪贴编辑」DNA——用限制酶当「剪刀」"
     "切下目的基因，用 DNA 连接酶当「胶水」把它拼到载体（质粒）上，导入受体生物"
     "表达。经典成果：①转基因抗虫棉（转入苏云金芽孢杆菌的 Bt 基因，自己「生产"
     "」杀虫蛋白，中国种植大面积推广）；②胰岛素/乙肝疫苗（把人胰岛素基因转入大"
     "肠杆菌/酵母大规模生产——比从动物胰腺提取便宜安全）；③ golden rice 黄金大"
     "米（转 β-胡萝卜素合成基因对抗维生素 A 缺乏）。安全与伦理：转基因食品需严"
     "格安全评价与标识（中国强制标识制度）；基因编辑婴儿（2018 年贺建奎事件）触"
     "碰伦理红线被严惩——技术无罪、应用有界。基因治疗（修正致病基因）是罕见病新"
     "希望。",
     ["转基因是怎么回事", "抗虫棉的原理", "转基因胰岛素为什么用细菌生产",
      "基因工程的步骤", "黄金大米是什么", "基因编辑婴儿为什么被禁止"],
     ["问 CRISPR 技术科普", "问转基因标识制度"],
     "atomic", "",
     "基因工程=限制酶剪切+连接酶拼接+载体导入受体表达；成果=Bt 抗虫棉/微生物产胰岛素·疫苗/黄金大米；安全=评价+强制标识；编辑婴儿=伦理红线严惩；CRISPR=新剪刀。"),
    ("kp_card_meiyu",
     "梅雨与伏旱",
     "人文通识知识点内容（人话接口）", "地理学",
     "梅雨：中国长江中下游地区（江淮流域）每年 6 月中旬至 7 月上旬的连绵阴雨天"
     "气——正值江南梅子成熟故名「梅雨」，也因衣物器具易发霉称「霉雨」。成因：夏"
     "季风北进，冷暖气团在江淮上空势均力敌形成**准静止锋**，雨带在此徘徊约一"
     "月。梅雨之后（7 月中-8 月）：雨带北移到华北，江淮被副热带高压控制，出现高"
     "温少雨的「伏旱」（三伏天）——「梅雨伏旱连着来」。对农业：梅雨利于插秧蓄"
     "水，但「空梅」（梅雨期极短）或「暴力梅」（暴雨成灾）都致灾；伏旱则需抗旱"
     "灌溉。日本南部（6 月梅雨/入梅）与韩国同期也有类似雨季。杜甫「梅雨」诗："
     "「湛湛长江去，冥冥细雨来」。",
     ["梅雨发生在什么季节", "梅雨的成因", "什么是伏旱", "空梅是什么",
      "准静止锋", "为什么梅雨之后是伏旱"],
     ["问雨带推移规律", "问副热带高压"],
     "atomic", "",
     "梅雨=6 月中-7 月上江淮连阴雨(梅子熟·衣物霉)：夏季风冷暖气团成准静止锋徘徊；之后雨带北移→副高控制现伏旱(三伏高温少雨)；空梅/暴力梅皆灾；日韩同期。"),
]

QUESTIONS = [
    ("QB-401", "宇航员在太空为什么漂浮", "物理学", "技术直答",
     ["失重", "自由落体"], "通识拓展67"),
    ("QB-402", "芯片的原料是什么", "化学", "技术直答",
     ["硅"], "通识拓展67"),
    ("QB-403", "转基因是怎么回事", "生物学", "技术直答",
     ["基因", "拼接", "重组DNA"], "通识拓展67"),
    ("QB-404", "梅雨发生在什么季节", "地理学", "技术直答",
     ["初夏", "6月", "江淮"], "通识拓展67"),
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
                               "level:L2", "status:verified", "batch:通识拓展67"],
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
    bank["version"] = "v1.59"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
