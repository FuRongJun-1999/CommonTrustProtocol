# -*- coding: utf-8 -*-
"""seed_common_585_cards.py · 通识拓展批次585知识卡+题库（幂等）

585：1 张新卡·谐音禁忌域（谐音禁忌与文化 kp_card_yinji——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1987~1989 可用）。
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
    ("kp_card_yinji",
     "谐音禁忌与文化",
     "民俗知识点内容（人话接口）", "传统文化",
     "谐音禁忌与文化——同一个音，两样心情：①**送礼禁忌**——不送钟（"
     "「送钟」谐「送终」）、情人不分梨（「分梨」谐「分离」）、不送伞（"
     "「伞」谐「散」）——谐音让礼物有了吉凶；②**数字迷信**——「4」"
     "谐「死」被楼栋车牌回避，「8」谐「发」、「6」谐「顺」、「9」谐「"
     "久」成抢手号；③**讨口彩**——年节食物取吉名：年糕「年年高」、鱼"
     "「年年有余」、苹果「平平安安」、枣花生桂圆莲子「早生贵子」；④**"
     "本命年扎红**——本命年系红腰带穿红衣辟邪祈福；⑤**理性看**——谐"
     "音禁忌无科学依据，却是语言塑造心理的文化现象，入乡随俗便是礼。",
     ["谐音禁忌", "送钟", "分梨", "数字禁忌",
      "讨口彩", "本命年"],
     ["问二十四节气", "问民俗"],
     "atomic", "",
     "谐音禁忌=不送钟送终情人不分梨分离不送伞散谐音定吉凶+4死8发6顺9"
     "久楼栋车牌回避+讨口彩年糕年年高鱼有余苹果平安枣生桂子+本命年扎红"
     "辟邪+无科学依据但语言塑心理入乡随俗是礼。"),
]

QUESTIONS = [
    ("QB-1987", "为什么不能送人钟？还有哪些送礼禁忌？",
     "传统文化", "技术直答",
     ["送钟", "送终", "禁忌", "送礼"], "通识拓展585·新卡"),
    ("QB-1988", "数字「4」和「8」的吉凶观念是怎么来的？",
     "传统文化", "技术直答",
     ["数字谐音", "4", "8", "迷信"], "通识拓展585·新卡"),
    ("QB-1989", "过年餐桌上的「讨口彩」有哪些讲究？",
     "传统文化", "技术直答",
     ["讨口彩", "年糕", "鱼", "苹果"], "通识拓展585·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展585"],
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
    bank["version"] = "v8.50"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
