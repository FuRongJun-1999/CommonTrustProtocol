# -*- coding: utf-8 -*-
"""seed_common_557_cards.py · 通识拓展批次557知识卡+题库（幂等）

557：1 张新卡·红楼梦典故域（红楼梦经典桥段 kp_card_hlm_dian——
    id 与语义等价卡名双重确认双零；金陵十二钗/宝黛关系 QB-1733 批
    与 QB-1743 已覆盖，本批立名场面角度不重复）。
预检已过（QB-1903~1905 可用）。
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
    ("kp_card_hlm_dian",
     "红楼梦经典桥段",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "红楼梦经典桥段——大观园里的悲欢：①**木石前盟与宝黛初会**——神"
     "瑛侍者日以甘露浇灌绛珠仙草，绛珠下凡以一生眼泪还他；宝玉初见黛玉"
     "便道「这个妹妹我曾见过的」；②**黛玉葬花**——见落花伤感，作《葬"
     "花吟》「花谢花飞花满天，红消香断有谁怜」，葬的是花也是身世；③**"
     "刘姥姥进大观园**——三进荣国府：一进打秋风受周济，二进宴席自嘲逗"
     "乐（「老刘老刘食量大如牛」），三进报恩救巧姐——朴实幽默与知恩图"
     "报；④**元妃省亲与抄检大观园**——为元春省亲建大观园是贾府极盛"
     "，抄检大观园则盛极而衰的转折；⑤**结构妙笔**——草蛇灰线伏脉千"
     "里，判词谶语处处埋伏笔。",
     ["黛玉葬花", "葬花吟", "刘姥姥进大观园", "木石前盟",
      "元妃省亲", "抄检大观园"],
     ["问金陵十二钗", "问红楼梦作者"],
     "atomic", "",
     "红楼梦桥段=木石前盟神瑛侍者浇灌绛珠还泪宝黛初见这个妹妹我曾见过"
     "+黛玉葬花花冢葬花吟花谢花飞红消香断葬花亦葬身世+刘姥姥三进荣国府"
     "打秋风逗乐救巧姐知恩图报+元妃省亲大观园极盛抄检大观园转衰+草蛇灰"
     "线伏脉千里判词谶语埋伏笔。"),
]

QUESTIONS = [
    ("QB-1903", "「黛玉葬花」是怎么回事？《葬花吟》名句是什么？",
     "文学常识", "技术直答",
     ["黛玉葬花", "葬花吟", "花谢花飞", "身世"], "通识拓展557·新卡"),
    ("QB-1904", "刘姥姥几次进荣国府？每次有什么不同？",
     "文学常识", "技术直答",
     ["刘姥姥", "荣国府", "大观园", "报恩"], "通识拓展557·新卡"),
    ("QB-1905", "「木石前盟」讲的是什么前世因缘？",
     "文学常识", "技术直答",
     ["木石前盟", "神瑛侍者", "绛珠仙草", "还泪"], "通识拓展557·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展557"],
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
    bank["version"] = "v8.22"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
