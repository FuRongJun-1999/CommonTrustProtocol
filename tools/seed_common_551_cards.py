# -*- coding: utf-8 -*-
"""seed_common_551_cards.py · 通识拓展批次551知识卡+题库（幂等）

551：1 张新卡·古建民居域（四合院与胡同 kp_card_siheyuan——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1885~1887 可用）。
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
    ("kp_card_siheyuan",
     "四合院与胡同",
     "传统建筑知识点内容（人话接口）", "传统文化",
     "四合院与胡同——老北京的城居肌理：①**四合院格局**——坐北朝南，"
     "北屋正房（长辈居）、东西厢房（晚辈）、南房倒座（客厅客房），四面"
     "围合中央庭院；按进深分单进、二进、三进乃至多进大院（「口日目」字"
     "形）；②**垂花门**——分隔内外院的「二门」，悬空垂柱雕莲花，旧话"
     "「大门不出二门不迈」的二门即它；③**影壁**——进门迎面短墙，与"
     "影壁照壁专卡呼应；④**胡同**——词源主流说为蒙古语「水井」，元代"
     "建大都时定型；北京俗语「著名的胡同三千六，没名的胡同赛牛毛」；"
     "南锣鼓巷、烟袋斜街是元代街巷格局的活标本；⑤**肌理**——胡同如"
     "脉络、四合院如细胞，共同构成老北京「灰墙灰瓦」的生活图景。",
     ["四合院", "胡同", "垂花门", "正房厢房",
      "南锣鼓巷", "胡同词源"],
     ["问影壁照壁", "问明式家具"],
     "atomic", "",
     "四合院胡同=坐北朝南北屋正房长辈东西厢房南房倒座围合庭院+单进二进"
     "三进口日目字形+垂花门二门分隔内外院悬空垂柱雕莲花+胡同蒙古语水井"
     "说元大都定型著名三千六没名赛牛毛+南锣鼓巷烟袋斜街活标本+胡同脉络"
     "四合院细胞灰墙灰瓦。"),
]

QUESTIONS = [
    ("QB-1885", "四合院的基本格局是怎样的？正房和厢房各住什么人？",
     "传统文化", "技术直答",
     ["四合院", "正房", "厢房", "格局"], "通识拓展551·新卡"),
    ("QB-1886", "四合院的「垂花门」在哪里？「大门不出二门不迈」的二门指它吗？",
     "传统文化", "技术直答",
     ["垂花门", "二门", "内外院", "四合院"], "通识拓展551·新卡"),
    ("QB-1887", "「胡同」这个词是怎么来的？有哪些著名胡同？",
     "传统文化", "技术直答",
     ["胡同", "蒙古语", "南锣鼓巷", "烟袋斜街"], "通识拓展551·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展551"],
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
    bank["version"] = "v8.16"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
