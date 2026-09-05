# -*- coding: utf-8 -*-
"""seed_common_226_cards.py · 通识拓展批次226知识卡+题库（幂等·三卡精批次）

226：传统文化-汤圆与元宵/传统文化-腊八粥/化学-腊八蒜为什么变绿
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_yuanxiao",
     "汤圆与元宵的区别",
     "人文通识知识点内容（人话接口）", "生活常识",
     "元宵节（正月十五）吃「元宵/汤圆」——**同名近亲但工艺不同**：①**元宵**"
     "（北方为主）——**滚**出来的：把固馅切块蘸水，在**干糯米粉**里反复滚动"
     "筛粉，一层层「滚厚」——表皮松、有嚼劲、煮后**汤浓**（糊化米粉入汤）；"
     "②**汤圆**（南方为主）——**包**出来的：湿糯米粉揉皮包馅收口——表皮光"
     "滑软糯、汤清。③**馅料**——元宵多为固体甜馅（黑芝麻/五仁），汤圆馅可"
     "甜可咸（鲜肉/花生/芝麻流心）。**通用提醒**：糯米黏滞难消化，老人小孩"
     "少量、趁热小口（凉了更黏更难消化）；3-4 个≈一碗米饭的热量。",
     ["汤圆和元宵的区别", "元宵是滚出来的", "汤圆是包出来的",
      "元宵节吃汤圆", "北方元宵南方汤圆"],
     ["问饺子（用饺子卡）", "问糯米消化"],
     "atomic", "",
     "元宵[北方]=干糯米粉滚出：表皮松有嚼劲汤浓、固馅为主；汤圆[南方]=湿皮包馅：光滑软糯汤清、甜咸均可；工艺差异=滚vs包；糯米黏滞难消化少量趁热吃，3-4 个≈一碗米饭热量。"),
    ("kp_card_labazhou",
     "腊八粥",
     "人文通识知识点内容（人话接口）", "生活常识",
     "腊八粥=**农历腊月初八**喝的传统粥：①**来源**——佛教「腊八节」纪念释"
     "迦牟尼成道（牧羊女献乳糜典故），寺院施粥演变为民间习俗；②**内容**——"
     "多种谷物豆类干果同熬：大米/小米/糯米+红豆/绿豆/芸豆+花生/莲子/桂圆/红"
     "枣——「七宝五味粥」各家配方不同；③**营养**——谷物豆类互补（谷物缺赖"
     "氨酸豆类补上），膳食纤维+B 族维生素丰富——是天然的「杂粮营养教科书」"
     "；④**节气意义**——腊八一到「过了腊八就是年」，年味从此开始。地区差异"
     "：北方甜粥为主，有些地方腊八还会泡**腊八蒜**。",
     ["腊八粥是哪一天", "腊八节的由来", "腊八粥有什么材料",
      "过了腊八就是年", "腊八粥的营养"],
     ["问腊八蒜（同日习俗）", "问杂粮营养"],
     "atomic", "",
     "腊八粥=农历腊月初八佛教成道日寺院施粥演变的民俗：多种谷物豆类干果同熬（七宝五味粥各家不同）；谷豆互补营养=天然杂粮教科书；过了腊八就是年——北方部分地区同日还泡腊八蒜。"),
    ("kp_card_labagarlic",
     "腊八蒜为什么变绿",
     "基础科学知识点内容（人话接口）", "化学",
     "腊八蒜=腊八这天泡的**绿瓣蒜**：①**变绿原理**——低温激活蒜中的**蒜酶"
     "，催化蒜氨酸反应先生成**蒜蓝素**（蓝色）再转化为**蒜黄素**（黄色），蓝"
     "+黄叠加呈**碧绿色**（类似天空蓝+黄调出绿的原理）；②**条件**——**低温"
     "**（腊八时节气温低正好）+**米醋**（酸性环境）+带皮蒜碎破坏细胞——所"
     "以要腊八泡、春节绿正好配饺子；③**安全**——绿色是蒜蓝素蒜黄素（无害"
     "硫化物），不是「有毒的绿」；④营养：保留大蒜素成分，刺激性比生蒜低。",
     ["腊八蒜为什么是绿的", "腊八蒜怎么泡", "腊八蒜变绿的原理",
      "蒜蓝素", "腊八蒜什么时候泡"],
     ["问大蒜素（蒜的化学）", "问春节饺子"],
     "atomic", "",
     "腊八蒜变绿=低温激活蒜酶：蒜氨酸→蒜蓝素[蓝]+蒜黄素[黄]叠加呈碧绿（无害硫化物非有毒）；条件=低温+米醋+细胞破坏——腊八泡春节绿配饺子；保留蒜素成分刺激比生蒜低。"),
]

QUESTIONS = [
    ("QB-877", "元宵和汤圆有什么区别？哪个是「滚」出来的哪个是「包」出来的？", "生活常识", "技术直答",
     ["北方", "滚", "干糯米粉", "南方", "包", "湿糯米粉"], "通识拓展226"),
    ("QB-878", "腊八粥是农历哪一天喝的？这个习俗与什么事件有关？", "生活常识", "技术直答",
     ["腊月初八", "腊八节", "佛教", "释迦牟尼", "施粥"], "通识拓展226"),
    ("QB-879", "腊八蒜为什么会变成绿色？变绿的大蒜还能吃吗？", "化学", "技术直答",
     ["蒜酶", "蒜蓝素", "蒜黄素", "低温", "米醋", "无害"], "通识拓展226"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展226"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.97"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
