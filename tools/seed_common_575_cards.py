# -*- coding: utf-8 -*-
"""seed_common_575_cards.py · 通识拓展批次575知识卡+题库（幂等）

575：1 张新卡·名茶谱系域（中国名茶谱 kp_card_mingcha——
    id 与语义等价卡名双重确认无独立卡；龙井归类 QB-1811
    已覆盖，本批立名茶谱系角度不重复）。
预检已过（QB-1957~1959 可用）。
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
    ("kp_card_mingcha",
     "中国名茶谱",
     "茶文化知识点内容（人话接口）", "传统文化",
     "中国名茶谱——一茶一山水：①**西湖龙井**（绿茶）——色绿香郁味甘"
     "形美「四绝」，狮峰为上；②**洞庭碧螺春**（绿茶）——太湖洞庭山，"
     "原名「吓煞人香」，康熙赐名；③**黄山毛峰**、**庐山云雾**——高山"
     "云雾出好茶；④**安溪铁观音**（乌龙）——「七泡有余香」；⑤**武夷"
     "大红袍**（岩茶之王）——母树生于九龙窠崖壁；⑥**祁门红茶**——与"
     "印度大吉岭、斯里兰卡乌瓦并称世界三大高香红茶；⑦**君山银针**（黄"
     "茶）——冲泡三起三落；⑧**云南普洱**（后发酵）——越陈越香；⑨**"
     "白毫银针**（白茶）——满披白毫如银似雪；⑩**口诀**——绿黄白青红"
     "黑，六色茶类各有名品。",
     ["中国名茶", "十大名茶", "西湖龙井", "碧螺春",
      "大红袍", "祁门红茶"],
     ["问中国茶文化", "问普洱茶"],
     "atomic", "",
     "名茶谱=西湖龙井色绿香郁味甘形美四绝狮峰为上+碧螺春吓煞人香康熙赐"
     "名太湖洞庭山+黄山毛峰庐山云雾高山云雾+铁观音七泡有余香+大红袍岩"
     "茶之王母树九龙窠+祁红世界三大高香红茶+君山银针三起三落黄茶+普洱"
     "越陈越香+白毫银针白茶+六色茶类各有名品。"),
]

QUESTIONS = [
    ("QB-1957", "中国有哪些著名的茶？西湖龙井有什么特点？",
     "传统文化", "技术直答",
     ["名茶", "西湖龙井", "四绝", "绿茶"], "通识拓展575·新卡"),
    ("QB-1958", "「岩茶之王」大红袍产自哪里？母树还有几株？",
     "传统文化", "技术直答",
     ["大红袍", "武夷山", "岩茶", "母树"], "通识拓展575·新卡"),
    ("QB-1959", "碧螺春的原名是什么？为什么改叫碧螺春？",
     "传统文化", "技术直答",
     ["碧螺春", "吓煞人香", "康熙", "洞庭山"], "通识拓展575·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展575"],
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
    bank["version"] = "v8.40"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
