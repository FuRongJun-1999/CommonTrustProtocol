# -*- coding: utf-8 -*-
"""seed_common_552_cards.py · 通识拓展批次552知识卡+题库（幂等）

552：1 张新卡·民居防御域（开平碉楼 kp_card_qiaolou——
    id 与语义等价卡名双重确认无独立卡；土楼 kp_card_tulou
    已有卡查重跳过）。
预检已过（QB-1888~1890 可用）。
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
    ("kp_card_qiaolou",
     "开平碉楼",
     "传统建筑知识点内容（人话接口）", "传统文化",
     "开平碉楼——华侨用钢筋水泥写下的家书：①**是什么**——广东江门开"
     "平市的防匪防洪多层塔楼式民居，清末民国华侨出资、融合多国建筑样式"
     "回乡兴建；②**中西合璧**——古罗马柱式、伊斯兰拱券、巴洛克穹顶与"
     "中式灰瓦飞檐同楼混搭，「万国建筑博览会」；③**实用功能**——厚墙"
     "铁窗、射击孔瞭望台防土匪，楼高地高避水患；④**世界遗产**——2007"
     " 年「开平碉楼与村落」（自力村、马降龙、锦江里、三门里）列入《世"
     "界遗产名录》，瑞石楼号称「开平第一楼」；⑤**客家民居呼应**——与"
     "福建土楼（详见专卡）、梅州围龙屋同为中国迁徙族群的聚居智慧结晶。",
     ["开平碉楼", "世界遗产", "中西合璧", "瑞石楼",
      "围龙屋", "华侨民居"],
     ["问福建土楼", "问四合院"],
     "atomic", "",
     "开平碉楼=广东江门开平清末民国华侨回乡建防匪防洪塔楼民居+古罗马柱"
     "伊斯兰拱券巴洛克穹顶中式飞檐混搭万国建筑博览会+厚墙铁窗射击孔避"
     "水患+2007开平碉楼与村落世界遗产自力村马降龙锦江里三门里瑞石楼第"
     "一楼+客家民居呼应土楼专卡梅州围龙屋。"),
]

QUESTIONS = [
    ("QB-1888", "开平碉楼是谁建的？为什么说它中西合璧？",
     "传统文化", "技术直答",
     ["开平碉楼", "华侨", "中西合璧", "江门"], "通识拓展552·新卡"),
    ("QB-1889", "开平碉楼被列入世界遗产是在哪一年？包括哪些村落？",
     "历史常识", "技术直答",
     ["开平碉楼", "2007", "世界遗产", "自力村"], "通识拓展552·新卡"),
    ("QB-1890", "客家民居有哪些代表？围龙屋和土楼有什么不同？",
     "传统文化", "技术直答",
     ["客家民居", "围龙屋", "土楼", "梅州"], "通识拓展552·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展552"],
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
    bank["version"] = "v8.17"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
