# -*- coding: utf-8 -*-
"""seed_common_431_cards.py · 通识拓展批次431知识卡+题库（幂等）

431：1 张新卡（八大菜系 kp_card_cuisines，题库卡库双零）
    + 2 张存量卡补题（淀粉与麦芽糖 kp_card_starchmalt 膳食纤维角度 /
    皮肤 kp_card_skin 晒太阳补钙角度，均已在库）。
KCCS 四要素+题干原句触发词。预检已过（QB-1531~1533 可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_cuisines",
     "八大菜系",
     "饮食文化知识点内容（人话接口）", "传统文化",
     "八大菜系——中国饮食文化的八大流派：①**四大菜系**（历史最久）——"
     "鲁菜（山东，宫廷菜基础，葱烧海参）、川菜（麻辣，麻婆豆腐/回锅肉）、"
     "粤菜（广东，清淡鲜美，白切鸡/早茶）、苏菜（淮扬菜，刀工精细，狮子"
     "头）；②**加四大菜系成八大**——浙菜（西湖醋鱼）、闽菜（佛跳墙）、"
     "湘菜（香辣，剁椒鱼头）、徽菜（臭鳜鱼）；③**地域逻辑**——「南甜"
     "北咸、东辣西酸」？实际更准确的说法是靠山吃山靠水吃水：物产与气候"
     "决定口味（川渝湿冷吃麻辣祛湿、沿海多海鲜重本味）；④**技法**——"
     "炒熘炸烹爆、蒸煮炖焖煨，中餐烹饪对火候的追求是「锅气」的灵魂。",
     ["八大菜系是哪八个", "川菜粤菜鲁菜苏菜", "中国菜系怎么分",
      "佛跳墙是哪个菜系", "淮扬菜特点", "中国饮食文化"],
     ["问饺子", "问茶文化"],
     "atomic", "",
     "八大菜系=鲁川粤苏四大加浙闽湘徽成八大+鲁菜宫廷葱烧海参川菜麻辣麻"
     "婆豆腐粤菜清淡早茶苏菜淮扬狮子头+浙西湖醋鱼闽佛跳墙湘剁椒鱼头徽"
     "臭鳜鱼+靠山吃山靠水吃食物产气候定口味+炒熘炸烹蒸煮炖焖锅气灵魂。"),
]

QUESTIONS = [
    ("QB-1531", "中国八大菜系是哪八个？它们各有什么代表菜？",
     "传统文化", "技术直答",
     ["八大菜系", "鲁菜", "川菜", "粤菜"], "通识拓展431"),
    ("QB-1532", "米饭越嚼越甜是怎么回事？人为什么不能消化纤维素？",
     "自然常识", "技术直答",
     ["淀粉", "麦芽糖", "唾液", "纤维素"], "通识拓展431·存量卡补题"),
    ("QB-1533", "人体最大的器官是什么？为什么晒太阳能补钙？",
     "健康与身体", "技术直答",
     ["皮肤", "器官", "晒太阳", "补钙"], "通识拓展431·存量卡补题"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展431"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v7.02"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
