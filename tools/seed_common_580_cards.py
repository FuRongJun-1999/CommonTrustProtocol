# -*- coding: utf-8 -*-
"""seed_common_580_cards.py · 通识拓展批次580知识卡+题库（幂等）

580：1 张新卡·发服政治域（辫发与剪辫 kp_card_bianfa——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1972~1974 可用）。
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
    ("kp_card_bianfa",
     "辫发与剪辫",
     "制度史知识点内容（人话接口）", "历史与文明",
     "辫发与剪辫——头发上的家国：①**剃发令**——清顺治二年（1645 年）"
     "颁令强制剃发结辫，「留头不留发，留发不留头」，江阴等地以「头可断"
     "，发决不可剃」抗令，辫发成为政治服从的标志；②**身体发肤**——古"
     "人观念「身体发肤，受之父母，不敢毁伤」（出自《孝经》），蓄发束髻"
     "是孝道体现，剃发「髡刑」是古代耻辱刑，「结发夫妻」喻原配；③**剪"
     "辫**——1911 年辛亥革命后剪辫成为革命符号，1912 年民国政府劝令剪"
     "辫，辫子从「顺民标志」变「旧时代尾巴」；④**启示**——一根头发牵"
     "动的是衣冠认同、政治服从与时代更替。",
     ["剃发令", "留头不留发", "身体发肤", "剪辫",
      "髡刑", "结发夫妻"],
     ["问清代官服等级", "问二十四节气"],
     "atomic", "",
     "辫发剪辫=清顺治二年1645剃发令留头不留发留发不留头江阴抗令辫发成"
     "服从标志+身体发肤受之父母孝经蓄发束髻髡刑耻辱刑结发夫妻喻原配+辛"
     "亥革命剪辫革命符号1912民国劝剪+一根头发牵动衣冠认同政治服从时代"
     "更替。"),
]

QUESTIONS = [
    ("QB-1972", "清初「剃发令」的内容是什么？「留头不留发」怎么理解？",
     "历史常识", "技术直答",
     ["剃发令", "留头不留发", "辫发", "顺治"], "通识拓展580·新卡"),
    ("QB-1973", "「身体发肤受之父母」出自哪里？髡刑是什么刑罚？",
     "传统文化", "技术直答",
     ["身体发肤", "孝经", "髡刑", "耻辱刑"], "通识拓展580·新卡"),
    ("QB-1974", "辛亥革命后的「剪辫」风潮意味着什么？",
     "历史常识", "技术直告",
     ["剪辫", "辛亥革命", "革命符号", "民国"], "通识拓展580·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展580"],
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
    bank["version"] = "v8.45"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
