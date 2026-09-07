# -*- coding: utf-8 -*-
"""seed_common_467_cards.py · 通识拓展批次467·存量卡补题（幂等）

467：3 张卡补 3 题（QB-1636~1638）——传统节日三连：春节与贴春联
    kp_card_springfestival / 腊八粥 kp_card_labazhou
    + 1 张新卡（重阳节 kp_card_chongyang，题库卡库双零）。
预检已过（QB-1636~1638 可用，三主题精确关键词 0 覆盖）。
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
    ("kp_card_chongyang",
     "重阳节",
     "传统节日知识点内容（人话接口）", "传统文化",
     "重阳节——农历九月初九的敬老节：①**由来**——《易经》以九为阳数，"
     "九月九日两九相重故称「重阳」；古有登高避灾的传说；②**习俗**——"
     "登高望远、赏菊、饮菊花酒、插茱萸——王维「遥知兄弟登高处，遍插"
     "茱萸少一人」写尽思亲之情；③**现代定位**——1989 年定为「老人节"
     "」，2013 年法定为老年节：九九谐音「久久」，寓意健康长寿，敬老"
     "爱老是节日的核心；④**过节方式**——陪长辈登高秋游、送上祝福、"
     "帮忙做一顿饭，把敬老落到日常。",
     ["重阳节是哪一天", "重阳节为什么登高", "遍插茱萸少一人",
      "重阳节和老人节", "菊花酒的寓意", "敬老节"],
     ["问中秋节", "问春节习俗"],
     "atomic", "",
     "重阳节=农历九月初九两九相重称重阳+登高望远赏菊饮菊花酒插茱萸王维"
     "遍插茱萸少一人+1989老人节2013法定老年节九九谐音久久长寿敬老爱老"
     "是核心+陪长辈登高秋游把敬老落到日常。"),
]

QUESTIONS = [
    ("QB-1636", "春节贴春联的习俗是怎么来的？最早的春联是什么？",
     "传统文化", "技术直答",
     ["春联", "桃符", "春节", "孟昶"], "通识拓展467·存量卡补题"),
    ("QB-1637", "腊八节为什么要喝腊八粥？腊八粥里有什么？",
     "传统文化", "技术直答",
     ["腊八粥", "腊八节", "寺庙", "七宝五味"], "通识拓展467·存量卡补题"),
    ("QB-1638", "重阳节是哪一天？有哪些传统习俗？",
     "传统文化", "技术直答",
     ["重阳节", "登高", "茱萸", "敬老"], "通识拓展467"),
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
                               "level:L2", "status:verified", "batch:通识拓展467"],
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
    bank["version"] = "v7.37"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
