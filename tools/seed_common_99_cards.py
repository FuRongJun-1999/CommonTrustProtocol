# -*- coding: utf-8 -*-
"""seed_common_99_cards.py · 通识拓展批次99知识卡+题库（幂等）

99：物理学-二力平衡/化学-溶液的酸碱度pH/生物学-细胞的生活需要物质和能量/地理学-长江的开发
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_2force",
     "二力平衡的条件",
     "基础科学知识点内容（人话接口）", "物理学",
     "物体在两个力作用下保持静止或匀速直线运动，这两个力**平衡**。二力平衡四条"
     "件（缺一不可）：①作用在**同一物体**上（同体）；②大小**相等**（等大）；③方"
     "向**相反**（反向）；④作用在**同一直线**上（共线）——口诀「同体、等大、反"
     "向、共线」。例：静止在桌上的书——重力与桌面支持力平衡；匀速下降的跳伞员—"
     "—重力与空气阻力平衡。易混辨析：平衡力 vs 相互作用力（相互作用力=作用在两"
     "个物体上，如书压桌子和桌子支持书）——最大区别在「是否同体」。应用：吊灯静"
     "止（拉力=重力）、匀速行驶的汽车（牵引力=阻力）。二力平衡是力学分析的基本工"
     "具：已知一个力可求另一个力。",
     ["二力平衡的条件是什么", "同体等大反向共线", "平衡力和相互作用力的区别",
      "匀速行驶的汽车受什么力", "静止的吊灯受力分析", "二力平衡应用"],
     ["问多力平衡扩展", "问平衡力与作用力反作用力对照表"],
     "atomic", "",
     "二力平衡四条件=同体+等大+反向+共线(缺一不可)：静止或匀速直线运动时用；与相互作用力的区别=是否作用在同一物体；应用=已知一力求另一力。"),
    ("kp_card_phscale",
     "溶液的酸碱度：pH",
     "基础科学知识点内容（人话接口）", "化学",
     "溶液的酸碱性强弱用 pH 表示，范围 **0~14**：pH<7 酸性（越小越酸，胃酸 pH≈"
     "1-3）；pH=7 中性（纯水）；pH>7 碱性（越大越碱，肥皂水≈10）。测定：pH 试纸"
     "（用玻璃棒蘸待测液滴到试纸上，与标准比色卡对照——**不能**把试纸浸入溶液，"
     "会污染试剂）；精密测定用 pH 计。生活相关：健康人体血液 pH 7.35-7.45（略偏"
     "碱）；雨水正常 pH≈5.6（溶有 CO₂），pH<5.6 为酸雨；洗发水弱碱性去油、护发"
     "素弱酸性闭合毛鳞片。注意：pH 只表示酸碱度强弱，与「是不是酸/碱物质」是两个"
     "概念；酸溶液稀释后 pH 变大但不会超过 7（无限稀释趋近 7）。",
     ["pH的范围是多少", "pH试纸怎么使用", "酸雨的pH是多少",
      "胃液的pH大约是多少", "酸性溶液稀释后pH怎么变", "人体血液的pH"],
     ["问 pH 计算稀释题", "问生活中常见物质 pH 表"],
     "atomic", "",
     "pH 0~14：<7 酸(胃液 1-3)/=7 中(纯水)/>7 碱(肥皂水 10)；试纸蘸液比对色卡（不浸入防污染）；酸雨<5.6；血液 7.35-7.45 稳定；酸液稀释 pH↑但趋 7 不过 7。"),
    ("kp_card_celllive",
     "细胞的生活需要物质和能量",
     "基础科学知识点内容（人话接口）", "生物学",
     "细胞是一个独立运转的「小工厂」：①物质进出——细胞膜控制物质进出（有用物"
     "质进入、废物排出、有用物质不易流出）；②能量转换的「动力车间」——**线粒"
     "体**：把有机物中的化学能释放供细胞利用（呼吸作用，动植物都有）；③光合「生"
     "产车间」——**叶绿体**（仅植物细胞）：把光能转成化学能储存在有机物中；④指"
     "挥中心——细胞核（含 DNA，控制遗传与代谢）。物质与能量的关系：细胞需要的物"
     "质（水/无机盐/糖类等）有的直接从外界获取，有的自己制造；能量储存在有机物"
     "中、由线粒体「燃烧」释放。细胞生活 = 物质交换 + 能量供应 + 信息调控（细胞"
     "核）三线并行。",
     ["细胞的生活需要什么", "线粒体和叶绿体的功能", "细胞膜控制物质进出",
      "细胞核的作用是什么", "动植物细胞都有线粒体吗", "细胞中的能量转换器"],
     ["问光合呼吸能量对比", "问细胞膜选择透过性"],
     "atomic", "",
     "细胞生活=膜控物质进出+线粒体释放能(呼吸·共有)+叶绿体储能(光合·植物独有)+细胞核调控(DNA)；能量转换器两件套；物质=水无机盐糖类等。"),
    ("kp_card_yangtzedevel",
     "长江的开发与治理",
     "人文通识知识点内容（人话接口）", "地理学",
     "长江（发源于唐古拉山，全长约 6300 公里，中国第一大河）开发与治理并重：**开"
     "发**——①水能：上游落差大水能富集，三峡工程（世界最大水电站）+葛洲坝；②"
     "航运：「黄金水道」——干流全年通航里程长，运量相当于多条铁路（宜宾以下四季"
     "通航）；③灌溉与供水（沿线城市群与农田）；④南水北调中线水源（丹江口）。**"
     "治理**——①洪涝：中下游「九曲回肠」荆江段泄洪不畅+围湖造田削弱调蓄，治理="
     "加固堤防/退田还湖/分洪工程/植树造林（上中游防护林）；②水污染治理（化工围江"
     "整治——「共抓大保护、不搞大开发」）；③十年禁渔（2021 起，恢复长江生态）。"
     "开发与保护平衡：生态优先、绿色发展。",
     ["长江水能资源集中在哪一段", "三峡工程的作用", "为什么长江被称为黄金水道",
      "长江洪涝灾害的原因", "长江十年禁渔", "长江的治理措施"],
     ["问黄河治理对比", "问三峡争议再评估"],
     "atomic", "",
     "长江开发=上游水能(三峡世界最大)+黄金水道+南水北调水源；治理=荆江防洪(堤防/退田还湖/防护林)+化工整治+十年禁渔；理念=共抓大保护不搞大开发。"),
]

QUESTIONS = [
    ("QB-529", "二力平衡的条件是什么", "物理学", "技术直答",
     ["同体", "等大", "反向", "共线"], "通识拓展99"),
    ("QB-530", "pH的范围是多少", "化学", "技术直答",
     ["0", "14", "0-14"], "通识拓展99"),
    ("QB-531", "细胞的生活需要什么", "生物学", "技术直答",
     ["物质", "能量"], "通识拓展99"),
    ("QB-532", "长江水能资源集中在哪一段", "地理学", "技术直答",
     ["上游"], "通识拓展99"),
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
                               "level:L2", "status:verified", "batch:通识拓展99"],
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
    bank["version"] = "v1.91"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
