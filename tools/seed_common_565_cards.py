# -*- coding: utf-8 -*-
"""seed_common_565_cards.py · 通识拓展批次565知识卡+题库（幂等）

565：1 张新卡·节气养生域（节气养生 kp_card_yusheng——
    id 与语义等价卡名双重确认双零；内容为民俗传统常识表述）。
预检已过（QB-1927~1929 可用）。
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
    ("kp_card_yusheng",
     "节气养生",
     "民俗养生知识点内容（人话接口）", "传统文化",
     "节气养生——顺时而养的民间传统（常识表述，健康问题请遵医嘱）："
     "①**春生**——「春捂」：初春别急着减衣；传统认为春季宜养肝、多踏"
     "青舒展；②**夏长**——「冬病夏治」：三伏天穴位敷贴（三伏贴）是中"
     "医传统做法；饮食清淡防暑湿；③**秋收**——「秋冻」适度耐寒锻炼，"
     "「贴秋膘」立秋吃肉补苦夏之亏，秋燥宜梨藕润肺；④**冬藏**——「冬"
     "令进补，来年打虎」：冬至起膏方进补，早卧晚起；⑤**俗谚**——「冬"
     "吃萝卜夏吃姜」「饭后百步走」（饭后宜缓行不宜剧烈）；「子午觉」："
     "子时大睡、午时小憩。以上均为民间养生传统，个体健康请以医生意见"
     "为准。",
     ["节气养生", "春捂秋冻", "冬病夏治", "贴秋膘",
      "冬令进补", "子午觉"],
     ["问二十四节气", "问数九与三伏"],
     "atomic", "",
     "节气养生=顺时而养常识表述遵医嘱+春捂初春缓减衣养肝踏青+夏三伏贴"
     "冬病夏治清淡防暑湿+秋冻适度耐寒贴秋膘补苦夏梨藕润肺+冬膏方进补"
     "早卧晚起+冬吃萝卜夏吃姜子午觉子时大睡午时小憩民间传统。"),
]

QUESTIONS = [
    ("QB-1927", "「春捂秋冻」是什么意思？有道理吗？",
     "传统文化", "技术直答",
     ["春捂", "秋冻", "节气", "养生"], "通识拓展565·新卡"),
    ("QB-1928", "「冬病夏治」和三伏贴是什么传统？",
     "传统文化", "技术直答",
     ["冬病夏治", "三伏贴", "传统", "中医"], "通识拓展565·新卡"),
    ("QB-1929", "「冬吃萝卜夏吃姜」这句俗谚怎么理解？",
     "传统文化", "技术直答",
     ["冬吃萝卜", "夏吃姜", "俗谚", "饮食"], "通识拓展565·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展565"],
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
    bank["version"] = "v8.30"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
