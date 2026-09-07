# -*- coding: utf-8 -*-
"""seed_common_442_cards.py · 通识拓展批次442·存量卡补题（幂等）

442：3 张卡补 3 题（QB-1564~1566）——中国名胜遗产三连：
    中国的世界文化遗产 kp_card_wcheritage / 敦煌莫高窟 kp_card_mogao
    + 1 张新卡（黄山与泰山 kp_card_huangtaishan，题库卡库双零）。
预检已过（QB-1564~1566 可用，三主题精确关键词 0 覆盖）。
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
    ("kp_card_huangtaishan",
     "黄山与泰山",
     "中国名胜知识点内容（人话接口）", "自然常识",
     "两座文化名山：①**黄山**（安徽）——「五岳归来不看山，黄山归来不"
     "看岳」，四绝：奇松（迎客松）、怪石、云海、温泉；徐霞客两次登临"
     "盛赞；1990 年列入世界文化与自然双遗产；②**泰山**（山东）——"
     "五岳之首（东岳），「会当凌绝顶，一览众山小」；历代帝王封禅之地"
     "——在泰山祭天宣告受命于天；1987 年中国首个世界文化与自然双"
     "遗产；③**对比**——黄山胜在自然景观奇绝，泰山胜在历史文化厚重；"
     "两者都是「双遗产」——自然景观与人文价值兼备的世界级名胜。",
     ["黄山四绝是什么", "黄山在哪", "泰山为什么是五岳之首",
      "迎客松", "封禅是什么", "徐霞客"],
     ["问华山", "问峨眉山"],
     "atomic", "",
     "黄山泰山=黄山安徽四绝奇松怪石云海温泉迎客松徐霞客两登1990双遗"
     "产+泰山山东五岳之首东岳会当凌绝顶历代帝王封禅祭天1987中国首个"
     "双遗产+黄山自然奇绝泰山文化厚重+两者自然人文兼备世界级名胜。"),
]

QUESTIONS = [
    ("QB-1564", "中国的世界文化遗产分哪几类？泰山是什么类型的遗产？",
     "地理常识", "技术直答",
     ["世界遗产", "文化遗产", "泰山", "双遗产"], "通识拓展442·存量卡补题"),
    ("QB-1565", "敦煌莫高窟以什么闻名？藏经洞是怎么发现的？",
     "历史常识", "技术直答",
     ["莫高窟", "敦煌", "壁画", "藏经洞"], "通识拓展442·存量卡补题"),
    ("QB-1566", "黄山「四绝」是什么？泰山为什么是五岳之首？",
     "地理常识", "技术直答",
     ["黄山", "泰山", "四绝", "五岳"], "通识拓展442"),
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
                               "level:L2", "status:verified", "batch:通识拓展442"],
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
    bank["version"] = "v7.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
