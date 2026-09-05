# -*- coding: utf-8 -*-
"""seed_common_211_cards.py · 通识拓展批次211知识卡+题库（幂等·两卡精批次）

211：生活常识-牙刷多久换一次/生活常识-砧板的卫生与保养
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（fridgeodor 卡仅
「旧牙刷」清洁工具一词提及）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_toothbrush",
     "牙刷多久换一次",
     "生活常识知识点内容（人话接口）", "生活常识",
     "牙刷更换规则：①**每 3 个月换一次**（即使刷毛没坏——刷毛根部滋生的细菌"
     "与磨耗的刷毛清洁力都下降）；②**刷毛外翻/开花立换**（外翻刷毛刷不到牙"
     "缝还伤牙龈）；③**感冒/生病痊愈后换**（牙刷残留病原体可能再次感染——"
     "口疮患者尤其）；④选购：**小头软毛**（小头能刷到后牙，硬毛伤牙龈牙本质"
     "）；⑤**存放**——刷头朝上竖放通风处沥干、**别用牙刷罩闷**（潮湿密闭滋"
     "菌）、**不与别人交叉接触**（一人一刷）；⑥电动牙刷刷头同样 3 个月一换"
     "（清洁效率高但刷头磨损同样快）。",
     ["牙刷多久换一次", "刷毛外翻还能用吗", "感冒后要换牙刷吗",
      "软毛牙刷好还是硬毛好", "牙刷怎么存放", "电动牙刷刷头多久换"],
     ["问巴氏刷牙法（用牙齿卡）", "问牙线使用"],
     "atomic", "",
     "牙刷=每 3 个月一换（根部滋菌+磨耗清洁力降）；刷毛外翻立换伤牙龈；感冒痊愈后换防再感染；选购小头软毛；存放刷头朝上竖放通风勿闷勿交叉；电动刷头同样 3 月一换。"),
    ("kp_card_cuttingboard",
     "砧板的卫生与保养",
     "生活常识知识点内容（人话接口）", "生活常识",
     "砧板是厨房交叉污染的最大源头：①**生熟分开**——至少两块：生肉一块/果蔬"
     "熟食一块（生肉的沙门氏菌/寄生虫通过砧板污染直接入口的熟食）；②**材质"
     "**——木质（护刀但易吸水发霉，需晾干）、竹制（硬度适中较不易霉）、塑料"
     "（可洗碗机但刀痕深藏菌——刀痕过深的**及时更换**）；③**清洁**——用后"
     "热水+洗洁精刷洗、**立放通风晾干**（平放闷着反面发霉）；每周盐粒+柠檬"
     "搓洗去味；深色霉斑刷不掉=更换（黄曲霉毒素风险）；④木砧板防裂——食品"
     "级矿物油定期涂抹。",
     ["砧板怎么消毒", "生熟砧板要分开吗", "木砧板发霉怎么办",
      "砧板多久换一次", "竹砧板和木砧板哪个好"],
     ["问生熟分开（用食品安全卡）", "问黄曲霉毒素"],
     "atomic", "",
     "砧板=交叉污染最大源头：生熟至少两块分开（生肉致病菌污染熟食）；用后热水洗立放晾干勿闷霉；每周盐+柠檬搓洗；霉斑刷不掉=更换（黄曲霉毒素）；木砧板食品级矿物油防裂。"),
]

QUESTIONS = [
    ("QB-847", "牙刷应该多久更换一次？什么情况下需要立即更换牙刷？", "生活常识", "技术直答",
     ["3个月", "三个月", "刷毛外翻", "感冒", "软毛"], "通识拓展211"),
    ("QB-848", "砧板为什么生熟要分开？木砧板发霉了还能用吗？", "生活常识", "技术直答",
     ["交叉污染", "生熟分开", "沙门氏菌", "晾干", "发霉", "更换"], "通识拓展211"),
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
                               "level:L2", "status:verified", "batch:通识拓展211"],
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
    bank["version"] = "v4.83"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
