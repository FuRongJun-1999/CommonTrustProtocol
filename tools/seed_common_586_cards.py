# -*- coding: utf-8 -*-
"""seed_common_586_cards.py · 通识拓展批次586知识卡+题库（幂等）

586：1 张新卡·本命年生肖民俗域（本命年与生肖民俗
    kp_card_benmingnian——id 与语义等价卡名双重确认双零；
    内容为民俗文化表述）。
预检已过（QB-1990~1992 可用）。
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
    ("kp_card_benmingnian",
     "本命年与生肖民俗",
     "民俗知识点内容（人话接口）", "传统文化",
     "本命年与生肖民俗——十二年一遇的红：①**本命年**——与自己出生生"
     "肖相同的流年，十二年一遇（12、24、36…岁）；②**民俗说法**——本"
     "命年「犯太岁」运势起伏，宜系红腰带、穿红衣、戴红绳以辟邪祈福，红"
     "色在中国文化中主喜庆避邪；③**生肖相合相冲**——民俗有「六冲」「"
     "六合」之说（如子午冲、子丑合），旧时婚配讲究属相，属民俗文化范畴"
     "并无科学依据；④**太岁**——本为纪年的岁星（木星）化身，民俗化"
     "为值年神，故有「太岁头上动土」的成语；⑤**生肖文化输出**——198"
     "0 年庚申猴票是新中国第一套生肖邮票、升值传奇，如今各国争发生肖邮"
     "票，生肖成为春节文化名片。",
     ["本命年", "犯太岁", "红腰带", "生肖相冲",
      "庚申猴票", "太岁头上动土"],
     ["问十二生肖", "问二十四节气"],
     "atomic", "",
     "本命年生肖=与出生生肖相同流年十二年一遇+犯太岁运势起伏民俗宜穿红"
     "扎红腰带红绳辟邪+生肖六冲六合婚配属相民俗无科学依据+太岁纪年岁星"
     "木星值年神太岁头上动土成语+1980庚申猴票第一套生肖邮票升值传奇各"
     "国争发生肖邮票春节名片。"),
]

QUESTIONS = [
    ("QB-1990", "本命年是怎么算的？有哪些民俗讲究？",
     "传统文化", "技术直答",
     ["本命年", "十二岁", "穿红", "民俗"], "通识拓展586·新卡"),
    ("QB-1991", "「犯太岁」和「太岁头上动土」是什么意思？",
     "传统文化", "技术直答",
     ["犯太岁", "太岁", "动土", "民俗"], "通识拓展586·新卡"),
    ("QB-1992", "新中国第一套生肖邮票是哪一年发行的？什么图案？",
     "传统文化", "技术直答",
     ["生肖邮票", "庚申猴票", "1980", "猴"], "通识拓展586·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展586"],
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
    bank["version"] = "v8.51"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
