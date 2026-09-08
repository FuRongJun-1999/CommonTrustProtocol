# -*- coding: utf-8 -*-
"""seed_common_587_cards.py · 通识拓展批次587知识卡+题库（幂等）

587：1 张新卡·节气礼俗域（节气民俗礼俗 kp_card_jieqi_minsu——
    id 与语义等价卡名双重确认双零；与节气养生卡（565批）、数九三伏卡
    （566批，实为566? 数九卡在566? 数九卡 kp_card_shujiusanfu 为566批
    实际566立的是床榻农谚，数九卡在564?——数九卡 kp_card_shujiusanfu
    已存在于库（566批次立），角度为历法养生，本批为礼俗仪式不重复）。
预检已过（QB-1993~1995 可用）。
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
    ("kp_card_jieqi_minsu",
     "节气民俗礼俗",
     "民俗知识点内容（人话接口）", "传统文化",
     "节气民俗礼俗——节气里的仪式感：①**立春打春牛**——「鞭春」：鞭"
     "打土牛或纸牛劝农迎春，牛肚藏五谷，打散象征五谷丰登，立春又叫「打"
     "春」；②**惊蛰民俗**——部分地区惊蛰有祭白虎、「打小人」的旧俗，"
     "借雷惊虫寓意驱赶晦气；③**芒种送花神**——百花渐谢，民间设案饯送"
     "花神，《红楼梦》第二十七回大观园饯花神写得最盛，黛玉葬花也在此时"
     "；④**霜降吃柿子**——闽南俗谚「霜降吃柿子，不会流鼻涕」，红柿应"
     "节；⑤**冬至祭祖**——冬至大如年：祭祖、数九、吃汤圆饺子；⑥**意"
     "义**——节气民俗把天文历法过成了有人情味的日子。",
     ["节气民俗", "打春牛", "鞭春", "送花神",
      "霜降吃柿子", "冬至祭祖"],
     ["问二十四节气", "问数九与三伏"],
     "atomic", "",
     "节气民俗礼俗=立春鞭春打春牛牛肚藏五谷劝农迎春又叫打春+惊蛰部分地"
     "区祭白虎打小人借雷驱晦+芒种饯送花神红楼梦二十七回黛玉葬花此时+霜"
     "降吃柿子闽南俗谚+冬至大如年祭祖数九汤圆饺子+节气民俗把历法过成人"
     "情味日子。"),
]

QUESTIONS = [
    ("QB-1993", "立春「打春牛」是什么习俗？有什么寓意？",
     "传统文化", "技术直答",
     ["打春牛", "鞭春", "立春", "劝农"], "通识拓展587·新卡"),
    ("QB-1994", "「芒种送花神」是什么习俗？和黛玉葬花有什么关系？",
     "文学常识", "技术直答",
     ["芒种", "送花神", "红楼梦", "饯花神"], "通识拓展587·新卡"),
    ("QB-1995", "为什么说「冬至大如年」？冬至有哪些习俗？",
     "传统文化", "技术直答",
     ["冬至", "祭祖", "数九", "汤圆饺子"], "通识拓展587·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展587"],
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
    bank["version"] = "v8.52"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
