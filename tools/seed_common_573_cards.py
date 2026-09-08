# -*- coding: utf-8 -*-
"""seed_common_573_cards.py · 通识拓展批次573知识卡+题库（幂等）

573：1 张新卡·古籍修复域（古籍修复 kp_card_guji_xiufu——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1951~1953 可用）。
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
    ("kp_card_guji_xiufu",
     "古籍修复",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "古籍修复——给古书当「医生」的手艺：①**原则**——「修旧如旧」、"
     "最小干预：能少动就少动，保留原书的历史信息；②**工序**——揭页、"
     "除尘清洗、补纸、托裱、齐栏、装订，一册虫蛀残书要经数十道工序；"
     "③**补纸讲究**——补纸的帘纹、厚薄、颜色须与原书匹配，「宁浅勿深"
     "」；④**浆糊**——修复用浆糊自制：小麦淀粉去筋熬制，稀而粘，讲究"
     "「薄浆水」；⑤**金镶玉**——一种装裱法：以宽大黄纸衬于旧页四周，"
     "黄白相映如金镶玉，既护书又美观；⑥**地位**——古籍修复技艺列入国"
     "家级非物质文化遗产，修复师被称作古书的「医生」。",
     ["古籍修复", "修旧如旧", "补纸", "金镶玉",
      "浆糊", "非遗"],
     ["问古籍装帧", "问善本收藏"],
     "atomic", "",
     "古籍修复=修旧如旧最小干预保留历史信息+揭页清洗补纸托裱齐栏装订数"
     "十道工序+补纸帘纹厚薄颜色匹配宁浅勿深+浆糊小麦淀粉去筋稀而粘+金"
     "镶玉宽黄纸衬旧页黄白相映+国家级非遗古书的医生。"),
]

QUESTIONS = [
    ("QB-1951", "古籍修复的「修旧如旧」是什么原则？",
     "传统文化", "技术直答",
     ["修旧如旧", "古籍修复", "最小干预", "原则"], "通识拓展573·新卡"),
    ("QB-1952", "「金镶玉」在古籍装裱里指什么？",
     "传统文化", "技术直答",
     ["金镶玉", "装裱", "衬纸", "古籍"], "通识拓展573·新卡"),
    ("QB-1953", "修复古籍的补纸有什么讲究？浆糊为什么要自己熬？",
     "传统文化", "技术直答",
     ["补纸", "帘纹", "浆糊", "去筋"], "通识拓展573·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展573"],
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
    bank["version"] = "v8.38"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
