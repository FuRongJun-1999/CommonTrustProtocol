# -*- coding: utf-8 -*-
"""seed_common_194_cards.py · 通识拓展批次194知识卡+题库（幂等·两卡精批次）

194：生活常识-飞蚊症/食品安全-木耳久泡中毒（米酵菌酸）
KCCS 四要素+题干原句触发词。三重预检：飞蚊症/木耳久泡中毒双库零覆盖
（「泡发」老卡实为生殖生理卡「卵泡发育」同名异物判定）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_floater",
     "飞蚊症",
     "生活常识知识点内容（人话接口）", "生活常识",
     "眼前有飘动的小黑点/细丝/蛛网，随眼球转动「飞来飞去」=**飞蚊症**：①**生"
     "理原因**——眼球内的**玻璃体**（凝胶状）随年龄**液化混浊**，其中的纤维"
     "碎片投影到视网膜上（近视者、40 岁以上更常见）——**多数是良性的**，会"
     "逐渐适应「无视」；②**危险信号（立即就医眼科）**：飞蚊**突然大量增多（"
     "如蝗虫群）**、伴**闪光感**（像闪电划过）、视野出现**黑幕遮挡**——这三"
     "联征提示**视网膜裂孔/脱离**（几小时内可致永久视力损伤）；③**区分口"
     "诀**：稳定少量=观察；突然增多+闪光+遮挡=急诊。高度近视者视网膜薄，发"
     "生率更高，应避免蹦极/拳击等剧烈震荡并定期查眼底。",
     ["飞蚊症是怎么回事", "眼前有黑点飘", "飞蚊症需要治疗吗",
      "视网膜脱离前兆", "飞蚊症危险信号"],
     ["问近视眼底检查", "问玻璃体手术"],
     "atomic", "",
     "飞蚊症=玻璃体液化混浊碎片投影（近视/40+常见多良性可适应）；危险三联征=突然大量增多+闪光感+视野黑幕遮挡→视网膜裂孔脱离急诊；高度近视视网膜薄避免剧烈震荡定期查眼底。"),
    ("kp_card_fungusacid",
     "木耳久泡为什么危险（米酵菌酸）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "木耳/银耳**长时间泡发（常温超过一天）**可能滋生**椰毒假单胞菌**，产生"
     "**米酵菌酸**——致死率最高的食源性毒素之一（50% 以上），且**耐热**：沸"
     "水煮、爆炒都**无法破坏**，中毒后无特效解毒药（损害肝肾脑，尚无特效解"
     "毒剂）。**安全规范**：①木耳/银耳/干蘑菇**冷水泡 1-2 小时**即可（最多"
     "不超过 4 小时）；②**泡发后如有异味/发黏/软烂立即丢弃**；③泡好后不及"
     "时吃就**冷藏并 24 小时内吃完**；④餐馆/摊位的凉拌木耳、长时间浸泡的湿"
     "米粉/河粉（同样风险）要谨慎。案例：多地发生家庭聚集性中毒死亡事件——"
     "「泡久了的木耳」不是浪费问题是**生死问题**。",
     ["木耳泡多久会中毒", "米酵菌酸是什么", "木耳久泡为什么危险",
      "泡发的木耳放几天还能吃吗", "椰毒假单胞菌"],
     ["问四季豆中毒（其他食源性）", "问干菇泡发"],
     "atomic", "",
     "木耳久泡常温超一天可滋生椰毒假单胞菌产米酵菌酸——致死率 50%+且耐热煮不死无特效解毒药；规范=冷水泡 1-2h（≤4h）+异味发黏即弃+泡好 24h 内吃完；湿米粉河粉同样风险——生死问题非浪费问题。"),
]

QUESTIONS = [
    ("QB-816", "眼前出现飘动的小黑点（飞蚊症）多数是什么原因？出现哪些信号必须立即就医？", "生活常识", "技术直答",
     ["玻璃体", "液化", "良性", "闪光感", "遮挡", "视网膜", "脱离"], "通识拓展194"),
    ("QB-817", "木耳泡发时间过长为什么可能致命？木耳的安全泡发时间是多久？", "生活常识", "技术直答",
     ["米酵菌酸", "椰毒假单胞菌", "耐热", "1-2小时", "4小时", "丢弃"], "通识拓展194"),
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
                               "level:L2", "status:verified", "batch:通识拓展194"],
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
    bank["version"] = "v4.67"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
