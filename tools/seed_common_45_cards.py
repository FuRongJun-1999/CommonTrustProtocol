# -*- coding: utf-8 -*-
"""seed_common_45_cards.py · 通识拓展批次45知识卡+题库（幂等）

45：物理学-能量转化/生活常识-海水为什么是咸的/生物学-果实的形成/历史-抗战胜利纪念日
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_energyconv",
     "能量的转化与守恒",
     "基础科学知识点内容（人话接口）", "物理学",
     "能量可以从一种形式转化为另一种形式（或在不同物体间转移），但总量保持不变"
     "——能量守恒定律，自然界最普遍的定律之一。常见转化：电风扇转动（电能→机械"
     "能）、电灯发光（电能→光能+内能）、摩擦生热（机械能→内能）、植物光合作用"
     "（光能→化学能）、水电站（水的重力势能→动能→电能）、电池充电（电能→化学"
     "能）、人体运动（化学能→机械能+热）。注意「消耗」电的准确说法是「转化」——"
     "能量不会凭空消失。效率永远小于 100%：总有一部分能量变成热散失（不能利用但"
     "依然守恒）。",
     ["电风扇转动时电能变成了什么能", "什么是能量守恒定律", "能量会消失吗",
      "光合作用是什么能转化成什么能", "水力发电的能量转化", "为什么效率不能100%"],
     ["问永动机为什么不可能", "问各种电站的能量链"],
     "atomic", "",
     "能量守恒=只转化转移不凭空生灭：风扇(电→机械)/光合(光→化学)/水电(势→动→电)；「消耗」=转化；效率<100% 因部分变热散失。"),
    ("kp_card_seawater",
     "海水为什么是咸的",
     "生活常识知识点内容（人话接口）", "生活常识",
     "海水约含 3.5% 的盐分（每千克海水约 35 克盐），主要是氯化钠，还有氯化镁等"
     "（镁盐让海水「苦咸」）。咸的来历：陆地上岩石土壤中的盐分被雨水亿万年级不"
     "断溶解，随河流搬运入海——水蒸发走了，盐留了下来，越积越咸（江河淡水也在"
     "带盐，只是浓度极低感觉不到）。为什么湖有咸有淡：只有出口的湖（外流湖）盐"
     "分随水流走是淡的；只进不出的封闭湖（内流湖，如青海湖、死海）水分蒸发盐留"
     "下，就变成咸湖——死海含盐约 30%，人躺上去不沉。海水不能直接喝（高渗脱水"
     "越喝越渴）。",
     ["海水为什么是咸的", "海水能喝吗", "死海为什么不沉人",
      "青海湖是淡水湖吗", "海水的盐度是多少", "淡水湖和咸水湖的区别"],
     ["问盐场晒盐原理", "问海洋盐度循环"],
     "atomic", "",
     "海水咸≈3.5%盐分：岩石盐分被雨水溶解经江河亿万年入海·蒸发留盐；外流湖淡/内流湖咸(死海30%不沉人)；海水高渗不能喝。"),
    ("kp_card_fruitform",
     "果实是怎么形成的",
     "基础科学知识点内容（人话接口）", "生物学",
     "开花后经过传粉（花粉落到柱头上）和受精（精子与胚珠结合），花的各部分开始"
     "变化：花瓣/雄蕊通常凋谢，子房发育成果实，胚珠发育成种子——苹果/桃的果肉"
     "其实是膨大的子房壁。日常易错点：我们吃的草莓表面的「籽」才是真正的果实"
     "（瘦果），红色部分是膨大的花托；无籽西瓜/无籽葡萄是人工培育（三倍体/激素"
     "处理）的结果；黄瓜茄子是果实（有种子），而甘蔗吃的是茎、萝卜吃的是根——"
     "「果实=子房发育而来+内含种子」是判定标准。种子的传播方式：风力（蒲公英）"
     "动物（苍耳挂毛/果实被吃后播种）、水力（椰子）、弹射（凤仙花）。",
     ["果实是怎么形成的", "果肉是花的哪部分发育的", "种子是胚珠发育来的吗",
      "草莓的籽是果实吗", "无籽西瓜为什么没有籽", "种子怎么传播"],
     ["问双子叶单子叶种子对比", "问人工授粉农业"],
     "atomic", "",
     "传粉受精后：子房→果实、胚珠→种子、花瓣雄蕊凋谢；果肉=子房壁；草莓红肉=花托·表面籽才是真果；无籽=三倍体/激素；传播=风/动物/水/弹射。"),
    ("kp_card_vday",
     "抗日战争胜利纪念日",
     "人文通识知识点内容（人话接口）", "历史",
     "中国人民抗日战争胜利纪念日是 9 月 3 日：1945 年 8 月 15 日日本天皇宣布无"
     "条件投降，9 月 2 日在东京湾密苏里号军舰上正式签署投降书——9 月 3 日举国"
     "庆祝，2014 年全国人大常委会以法律形式确定 9 月 3 日为纪念日。抗战历时 14 "
     "年（1931 九一八事变局部抗战→1937 七七事变全面抗战），中国军民伤亡 3500 "
     "万以上。相关纪念日：7 月 7 日（全民族抗战爆发/七七事变）、12 月 13 日（南"
     "京大屠杀死难者国家公祭日，1937 年 30 万同胞遇难）、9 月 18 日（九一八事变"
     "警报长鸣）。2015 年、2025 年均举行胜利日阅兵。",
     ["抗日战争胜利纪念日是哪一天", "日本宣布投降是哪天", "抗战一共打了多少年",
      "国家公祭日是哪一天", "九一八事变是哪一年", "为什么是9月3日"],
     ["问抗战重要战役", "问二战各国纪念日"],
     "atomic", "",
     "胜利纪念日=9月3日(1945.8.15 宣布投降·9.2 签降书·9.3 庆祝·2014 立法)；抗战 14 年(1931-1945)·伤亡 3500 万+；公祭日=12.13(南京)。"),
]

QUESTIONS = [
    ("QB-313", "电风扇转动时电能变成了什么能", "物理学", "技术直答",
     ["机械能"], "通识拓展45"),
    ("QB-314", "海水为什么是咸的", "生活常识", "技术直答",
     ["盐分", "溶解"], "通识拓展45"),
    ("QB-315", "果实是怎么形成的", "生物学", "技术直答",
     ["子房", "受精"], "通识拓展45"),
    ("QB-316", "抗日战争胜利纪念日是哪一天", "历史", "技术直答",
     ["9月3日"], "通识拓展45"),
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
                               "level:L2", "status:verified", "batch:通识拓展45"],
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
    bank["version"] = "v1.37"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
