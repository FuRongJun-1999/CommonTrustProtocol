# -*- coding: utf-8 -*-
"""seed_common_574_cards.py · 通识拓展批次574知识卡+题库（幂等）

574：1 张新卡·茶器域（建盏与宋代茶器 kp_card_jianzhan——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1954~1956 可用）。
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
    ("kp_card_jianzhan",
     "建盏与宋代茶器",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "建盏与宋代茶器——黑釉里的星河：①**建盏**——福建建阳水吉镇烧制"
     "的黑釉茶碗，宋徽宗《大观茶论》盛赞；②**釉色三绝**——兔毫（细密"
     "如兔毛毫纹）、油滴（银蓝斑点如油珠）、曜变（黑釉中晕出虹彩光圈，"
     "传世完整器仅数件且多藏于日本，被奉为国宝）；③**为什么是黑的**——"
     "宋代盛行点茶：茶饼碾末注汤击拂出白沫，黑釉最能衬茶色白、便于「咬"
     "盏」斗茶；④**斗茶与茶百戏**——比汤色、验水痕，高手还能在茶沫上"
     "作画称「茶百戏」；⑤**地位**——建窑建盏烧制技艺列入国家级非遗，"
     "建盏复兴成为当代茶器热门。",
     ["建盏", "兔毫", "油滴", "曜变天目", "点茶",
      "斗茶"],
     ["问中国茶文化", "问紫砂壶"],
     "atomic", "",
     "建盏=福建建阳水吉镇黑釉茶碗大观茶论盛赞+兔毫油滴曜变三绝曜变传世"
     "极罕多藏日本+宋代点茶茶末注汤击拂白沫黑釉衬茶色咬盏斗茶+茶百戏茶"
     "沫作画+建窑建盏技艺国家级非遗当代茶器热门。"),
]

QUESTIONS = [
    ("QB-1954", "建盏是什么？兔毫、油滴、曜变分别指什么？",
     "传统文化", "技术直答",
     ["建盏", "兔毫", "油滴", "曜变"], "通识拓展574·新卡"),
    ("QB-1955", "宋代的点茶和斗茶是怎么玩的？",
     "传统文化", "技术直答",
     ["点茶", "斗茶", "击拂", "咬盏"], "通识拓展574·新卡"),
    ("QB-1956", "为什么宋代茶碗多是黑色的？",
     "传统文化", "技术直答",
     ["黑釉", "茶色", "宋代", "建盏"], "通识拓展574·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展574"],
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
    bank["version"] = "v8.39"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
