# -*- coding: utf-8 -*-
"""seed_common_409_cards.py · 通识拓展批次409知识卡+题库（幂等）

409：2 张存量卡补题（文艺复兴 kp_card_renaissance /
    工业革命 kp_card_industrialrev，均已在库）
    + 1 张新卡（圣诞节与世界节日 kp_card_christmas，双零）。
KCCS 四要素+题干原句触发词。预检已过（QB-1465~1467 可用，
文艺复兴/工业革命/圣诞节题库 0 覆盖）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("kp_card_christmas",
     "圣诞节与世界节日",
     "世界文化知识点内容（人话接口）", "世界文化",
     "圣诞节——西方最重要的传统节日：①**来历**——纪念耶稣基督诞生，"
     "定在 12 月 25 日（公元纪年也以耶稣诞生年为起点）；「圣诞前夜」"
     "12 月 24 日晚称为平安夜；②**典型符号**——圣诞老人（原型是公元"
     "4 世纪乐善好施的圣·尼古拉斯主教）、圣诞树（常青树象征生命）、"
     "圣诞礼物装进袜子挂在床头（源自尼古拉斯暗中赠金的故事）、驯鹿雪"
     "橇；③**节日经济**——圣诞季是西方全年最大的消费季，「节日祝福+"
     "礼物交换」成为重要社交文化；④**其他世界节日**——万圣节（10 月"
     "31 日，南瓜灯与「不给糖就捣蛋」）、感恩节（11 月第四个周四，火"
     "鸡大餐，源自清教徒丰收感恩）、复活节（春分月圆后第一个星期日，"
     "彩蛋象征新生）。",
     ["圣诞节是怎么来的", "圣诞老人的原型", "平安夜是什么",
      "万圣节南瓜灯", "感恩节火鸡", "世界主要节日"],
     ["问中秋节", "问春节"],
     "atomic", "",
     "圣诞节=纪念耶稣诞生12月25日平安夜24日晚+圣诞老人原型圣尼古拉斯"
     "主教圣诞树常青礼物装袜子+圣诞季全年最大消费季+万圣节南瓜灯不给"
     "糖就捣蛋+感恩节十一月第四个周四火鸡+复活节彩蛋新生。"),
]

QUESTIONS = [
    ("QB-1465", "什么是文艺复兴？文艺复兴三杰是谁？",
     "世界历史", "技术直答",
     ["文艺复兴", "人文主义", "达芬奇", "三杰"], "通识拓展409·存量卡补题"),
    ("QB-1466", "第一次工业革命的标志是什么？四次工业革命分别是什么时代？",
     "世界历史", "技术直答",
     ["工业革命", "蒸汽机", "电气", "智能"], "通识拓展409·存量卡补题"),
    ("QB-1467", "圣诞节是怎么来的？圣诞老人的原型是谁？",
     "世界文化", "技术直答",
     ["圣诞节", "圣诞老人", "平安夜", "节日"], "通识拓展409"),
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
                               "level:L2", "status:verified", "batch:通识拓展409"],
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
    bank["version"] = "v6.80"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
