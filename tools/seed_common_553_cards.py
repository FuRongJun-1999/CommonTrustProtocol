# -*- coding: utf-8 -*-
"""seed_common_553_cards.py · 通识拓展批次553知识卡+题库（幂等）

553：1 张新卡 + 1 张存量卡补题·家训园林域
    （家训文化 kp_card_jiaxun 新卡——id 与语义等价卡名双重确认双零；
    苏州园林手法补题挂 kp_card_suzhougarden——框景/移步换景角度
    与 QB-1224 借景题不重复）。
预检已过（QB-1891~1893 可用）。
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
    ("kp_card_jiaxun",
     "家训文化",
     "传统文化知识点内容（人话接口）", "传统文化",
     "家训文化——写在书里的家风：①**《颜氏家训》**——南北朝颜之推著"
     "，二十篇，被誉为「古今家训之祖」（颜真卿即其后人）；②**《朱子家"
     "训》**——明末清初朱用纯（柏庐）著，「黎明即起，洒扫庭除」「一粥"
     "一饭，当思来处不易；半丝半缕，恒念物力维艰」几乎人人能诵；③**《"
     "曾国藩家书》**——千余封家信讲修身齐家教子，「家俭则兴，人勤则健"
     "」；④**《傅雷家书》**——现代翻译家写给儿子傅聪的信，先做人再做"
     "艺术家；⑤**意义**——家训是家庭的精神契约，「忠厚传家久，诗书继"
     "世长」，家风正则子孙正。",
     ["家训", "颜氏家训", "朱子家训", "曾国藩家书",
      "傅雷家书", "家风"],
     ["问避讳文化", "问科举制度"],
     "atomic", "",
     "家训文化=颜氏家训南北朝颜之推古今家训之祖颜真卿后裔+朱子家训朱用"
     "纯黎明即起一粥一饭当思来处不易+曾国藩家书千余封家俭则兴人勤则健+"
     "傅雷家书先做人再做艺术家+家训家庭精神契约忠厚传家久诗书继世长。"),
]

QUESTIONS = [
    ("QB-1891", "《颜氏家训》为什么被称为「古今家训之祖」？作者是谁？",
     "传统文化", "技术直答",
     ["颜氏家训", "颜之推", "家训之祖", "南北朝"], "通识拓展553·新卡"),
    ("QB-1892", "「一粥一饭当思来处不易」出自哪部家训？作者是谁？",
     "传统文化", "技术直答",
     ["朱子家训", "朱柏庐", "一粥一饭", "俭"], "通识拓展553·新卡"),
    ("QB-1893", "园林中的「框景」和「移步换景」是什么手法？",
     "传统文化", "技术直答",
     ["框景", "移步换景", "苏州园林", "造园"], "通识拓展553·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展553"],
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
    bank["version"] = "v8.18"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
