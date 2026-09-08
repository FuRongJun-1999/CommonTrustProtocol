# -*- coding: utf-8 -*-
"""seed_common_571_cards.py · 通识拓展批次571知识卡+题库（幂等）

571：1 张新卡·冰雪雅俗域（冰嬉与消寒会 kp_card_bingxi——
    id 与语义等价卡名双重确认双零；数九三伏卡覆盖历法角度，
    本批立冰上运动与文人雅集角度不重复）。
预检已过（QB-1945~1947 可用）。
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
    ("kp_card_bingxi",
     "冰嬉与消寒会",
     "民俗雅玩知识点内容（人话接口）", "传统文化",
     "冰嬉与消寒会——古人的冬日玩乐：①**冰嬉**——清代宫廷冰上运动"
     "的总称，乾隆时定为「国俗」：每年冬季在太液池（今北海）校阅八旗冰"
     "鞋营，项目有抢等（速滑比赛）、抢球、转龙射球（滑行中张弓射彩球）；"
     "②**《冰嬉图》**——清宫廷画家绘长卷，故宫博物院藏，记录千百人冰"
     "上竞技的盛况——堪称古代「冬奥」影像；③**冰床**——木板钉铁条为"
     "底，人拉或杆撑滑行，是旧时北京什刹海、护城河上的「冰上出租」；"
     "④**消寒会**——文人冬至后九九八十一天里轮流做东的雅集，饮酒赋诗"
     "联句，以文会友熬过寒冬；⑤**意义**——冰雪游戏与文墨雅集，是北方"
     "冬日限定的生活方式。",
     ["冰嬉", "冰嬉图", "太液池", "冰床",
      "消寒会", "抢等"],
     ["问数九与三伏", "问二十四节气"],
     "atomic", "",
     "冰嬉消寒会=清代宫廷冰上运动乾隆定国俗太液池校阅八旗冰鞋营+抢等"
     "速滑抢球转龙射球+冰嬉图故宫藏千人造况+冰床木板铁条什刹海冰上出租"
     "+消寒会文人九九轮流做东饮酒赋诗+北方冬日限定生活。"),
]

QUESTIONS = [
    ("QB-1945", "「冰嬉」是什么运动？为什么说它是清代国俗？",
     "传统文化", "技术直答",
     ["冰嬉", "清代", "太液池", "冰鞋营"], "通识拓展571·新卡"),
    ("QB-1946", "古代的「冰床」是什么？在哪里能玩到？",
     "传统文化", "技术直答",
     ["冰床", "什刹海", "滑行", "冬季"], "通识拓展571·新卡"),
    ("QB-1947", "「消寒会」是什么聚会？文人在冬天怎么消遣？",
     "传统文化", "技术直答",
     ["消寒会", "文人", "九九", "雅集"], "通识拓展571·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展571"],
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
    bank["version"] = "v8.36"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
