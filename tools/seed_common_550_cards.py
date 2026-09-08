# -*- coding: utf-8 -*-
"""seed_common_550_cards.py · 通识拓展批次550知识卡+题库（幂等）

550：1 张新卡·茶馆文化域（茶馆文化 kp_card_chaguan——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1882~1884 可用）。
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
    ("kp_card_chaguan",
     "茶馆文化",
     "传统文化知识点内容（人话接口）", "传统文化",
     "茶馆文化——一盏茶里的市井江湖：①**文学名片**——老舍话剧《茶馆"
     "》三幕写尽三个时代，裕泰茶馆王利发成了国民记忆；②**成都茶馆**——"
     "「坐茶馆」是生活方式：盖碗茶三件套（茶盖、茶碗、茶船）、长嘴铜壶"
     "隔桌掺茶的功夫、竹椅龙门阵、掏耳朵采耳，鹤鸣茶社百年不歇；③**北"
     "京大碗茶**——二分钱一碗的街头大碗茶，尹盛喜从前门大碗茶起家创办"
     "老舍茶馆（1988），京味名片；④**社会功能**——茶馆是信息集散地："
     "茶座、书场、下棋、谈生意，江南旧俗「吃讲茶」——纠纷双方上茶馆当"
     "众评理调解；⑤**如今**——茶馆从市井走向雅集，围炉煮茶成新风尚。",
     ["茶馆文化", "老舍茶馆", "盖碗茶", "大碗茶",
      "吃讲茶", "鹤鸣茶社"],
     ["问茶文化", "问传统婚俗"],
     "atomic", "",
     "茶馆文化=老舍茶馆三幕三时代裕泰王利发国民记忆+成都坐茶馆盖碗三件"
     "套长嘴铜壶掺茶龙门阵采耳鹤鸣茶社百年+北京二分钱大碗茶尹盛喜起家老"
     "舍茶馆1988京味名片+信息集散茶座书场谈生意吃讲茶评理+围炉煮茶新风"
     "尚。"),
]

QUESTIONS = [
    ("QB-1882", "老舍的话剧《茶馆》讲了什么？为什么是经典？",
     "文学常识", "技术直答",
     ["老舍", "茶馆", "话剧", "裕泰"], "通识拓展550·新卡"),
    ("QB-1883", "成都茶馆的盖碗茶三件套指什么？长嘴壶掺茶有什么讲究？",
     "传统文化", "技术直答",
     ["盖碗茶", "茶盖", "长嘴壶", "成都"], "通识拓展550·新卡"),
    ("QB-1884", "老北京「大碗茶」和「吃讲茶」分别是什么习俗？",
     "传统文化", "技术直答",
     ["大碗茶", "吃讲茶", "老舍茶馆", "茶馆"], "通识拓展550·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展550"],
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
    bank["version"] = "v8.15"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
