# -*- coding: utf-8 -*-
"""seed_common_437_cards.py · 通识拓展批次437知识卡+题库（幂等）

437：2 张存量卡补题（中国古典诗词 kp_card_classicalpoetry：李白杜甫
    苏轼角度，已在库）+ 1 张新卡（鲁迅与白话文文学 kp_card_luxun，
    题库卡库双零）。文学巨匠三连。
预检已过（QB-1549~1551 可用，三主题精确关键词 0 覆盖）。
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
    ("kp_card_luxun",
     "鲁迅与白话文文学",
     "文学常识知识点内容（人话接口）", "传统文化",
     "鲁迅（1881-1936）——中国现代文学的奠基人：①**新文化运动旗手**——"
     "1918 年发表《狂人日记》，中国第一篇现代白话小说，猛烈批判封建"
     "礼教「吃人」；②**代表作品**——小说集《呐喊》《彷徨》（《阿Q正"
     "传》《祝福》）、散文集《朝花夕拾》、散文诗集《野草》、大量杂文；"
     "③**人物塑造**——阿Q（精神胜利法）、闰土、祥林嫂、孔乙己——个个"
     "是国民性的镜子；④**名言**——「横眉冷对千夫指，俯首甘为孺子牛」"
     "「世上本没有路，走的人多了，也便成了路」；⑤**地位**——毛泽东"
     "评价「鲁迅的方向，就是中华民族新文化的方向」。",
     ["鲁迅的代表作品", "狂人日记的意义", "阿Q正传讲什么",
      "中国现代文学奠基人", "白话文运动", "朝花夕拾"],
     ["问老舍", "问茅盾"],
     "atomic", "",
     "鲁迅=中国现代文学奠基人新文化运动旗手+1918狂人日记第一篇现代白"
     "话小说批判礼教吃人+呐喊彷徨朝花夕拾野草杂文+阿Q精神胜利法闰土"
     "祥林嫂孔乙己国民性镜子+横眉冷对千夫指俯首甘为孺子牛+鲁迅的方向"
     "就是中华民族新文化的方向。"),
]

QUESTIONS = [
    ("QB-1549", "「诗仙」和「诗圣」分别是谁？唐诗宋词有什么地位？",
     "文学常识", "技术直答",
     ["李白", "杜甫", "诗仙", "诗圣"], "通识拓展437·存量卡补题"),
    ("QB-1550", "宋词的豪放派和婉约派代表人物分别是谁？",
     "文学常识", "技术直答",
     ["宋词", "豪放派", "婉约派", "苏轼"], "通识拓展437·存量卡补题"),
    ("QB-1551", "鲁迅的代表作有哪些？《狂人日记》有什么历史意义？",
     "文学常识", "技术直答",
     ["鲁迅", "狂人日记", "白话文", "阿Q"], "通识拓展437"),
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
                               "level:L2", "status:verified", "batch:通识拓展437"],
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
    bank["version"] = "v7.08"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
