# -*- coding: utf-8 -*-
"""seed_common_220_cards.py · 通识拓展批次220知识卡+题库（幂等·两卡精批次）

220：生活常识-食用油的储存/趣味科学-耳机线为什么总打结
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_oilstoring",
     "食用油的储存",
     "生活常识知识点内容（人话接口）", "生活常识",
     "食用油变质的两大杀手=**光照+高温**（氧化酸败：产生哈喇味+有害氧化产"
     "物）。**正确储存**：①**避光**——放橱柜里，别放窗台灶台边（透明瓶尤其"
     "怕光，选深色瓶更好）；②**远离热源**——别放在灶台旁（每次炒菜的高温都"
     "在加速氧化）；③**密封**——用完拧紧瓶盖（接触空气越多氧化越快）；④**"
     "开封后 3 个月内用完**（大桶油建议分装小瓶+大桶密封避光）；⑤**勿新油"
     "兑旧油**（旧油中的氧化产物会加速新油变质）；⑥低温变浑浊凝固是物理现"
     "象（花生油冬天尤明显），回温即恢复不影响品质。**哈喇味=已酸败，丢弃勿"
     "再吃**（氧化产物伤血管肝脏）。",
     ["食用油怎么储存", "开封的油能放多久", "油为什么会有哈喇味",
      "油壶放哪里好", "花生油冬天凝固", "油壶要不要洗"],
     ["问酱油储存（用酱油卡）", "问油脂健康"],
     "atomic", "",
     "食用油储存=避光（放橱柜选深色瓶）+远离灶台热源+密封拧紧+开封 3 个月用完+勿新油兑旧油；低温浑浊凝固=物理现象回温恢复；哈喇味=已酸败有害丢弃勿吃——氧化产物伤血管肝脏。"),
    ("kp_card_earphoneknot",
     "耳机线为什么总打结",
     "基础科学知识点内容（人话接口）", "数学",
     "耳机线放口袋里几乎**必然打结**——这有数学研究支撑：①2007 年物理学家"
     "用实验证明：把软绳放进盒子里**摇动几秒钟**就会自发形成结（概率超 50%"
     "）；②**原理**——长软线在有限空间里随机盘绕时，存在的**组合状态数量巨"
     "大**，其中「打了结」的状态占绝大多数（数学上三叶结等结型数量远多于无"
     "结平放态）；③线越长越软、盒子越颠簸，打结概率越高——耳机线长度（约 "
     "1.3m）恰好是「重灾区」。**防结技巧**：a.**绕成圈**收纳（松绕成环用绑"
     "带固定）；b.用**绕线器/收纳盒**；c.无线耳机根治。冷知识：无绳化的蓝牙"
     "耳机从数学上「消灭」了这个结论问题。",
     ["耳机线为什么总打结", "耳机打结原理", "怎么收纳耳机不打结",
      "墨菲定律耳机", "绕线技巧"],
     ["问墨菲定律", "问无线耳机"],
     "atomic", "",
     "耳机线打结有数学研究：长软线在盒内随机盘绕，「有结」的组合态占绝大多数（2007 实验 50%+概率打结）；线越软越长越颠簸越易结——1.3m 耳机线是重灾区；防结=绕圈收纳/绕线器，无线根治。"),
]

QUESTIONS = [
    ("QB-863", "食用油应该怎么储存才能延缓变质？为什么哈喇味的油不能吃？", "生活常识", "技术直答",
     ["避光", "热源", "密封", "开封", "3个月", "哈喇味", "酸败"], "通识拓展220"),
    ("QB-864", "耳机线放口袋里为什么容易打结？有什么防打结的收纳技巧？", "数学", "技术直答",
     ["随机", "组合", "概率", "绕圈", "收纳", "绕线器"], "通识拓展220"),
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
                               "level:L2", "status:verified", "batch:通识拓展220"],
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
    bank["version"] = "v4.90"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
