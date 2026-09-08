# -*- coding: utf-8 -*-
"""seed_common_522_cards.py · 通识拓展批次522知识卡+题库（幂等）

522：1 张新卡 + 1 张存量卡补题·影偶演艺域
    （木偶戏 kp_card_muou 新卡——id 与语义等价卡名双重确认双零；
    皮影材料补题挂 kp_card_pshadow——与 QB-983 表演历史题不重复）。
预检已过（QB-1798~1800 可用）。
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
    ("kp_card_muou",
     "木偶戏",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "木偶戏——「傀儡戏」的千年掌上乾坤：①**古称与源流**——古称傀儡"
     "戏，汉代已有偶人作戏记载，唐宋大盛（宋代市井「悬丝傀儡」「杖头"
     "傀儡」皆有专棚）；②**四大类**——提线木偶（悬丝傀儡：线系全身，"
     "泉州提线木偶线可多达三十余条，能写字划酒）、布袋木偶（掌中木偶"
     "：一人一掌一台戏，闽南漳州泉州「布袋戏」）、杖头木偶（杖杆托举，"
     "南北皆广）、铁枝木偶（潮汕，铁枝操纵躯干，似皮影立体版）；③**"
     "绝活**——泉州木偶《驯猴》能搬箱写字，布袋戏一双手同时演生旦净"
     "丑；④**非遗**——漳州布袋木偶戏、泉州提线木偶戏等均列入国家级非"
     "物质文化遗产；⑤**意义**——「以偶代人」，操偶师十指连心，是东方"
     "「手办动画」的活化石。",
     ["木偶戏有哪几类", "提线木偶", "布袋戏", "傀儡戏",
      "泉州木偶", "掌中木偶"],
     ["问皮影戏", "问京剧"],
     "atomic", "",
     "木偶戏=傀儡戏汉代已载唐宋大盛宋代专棚+提线悬丝泉州三十余线能写"
     "字+布袋掌中一人一掌一台戏漳州泉州+杖头托举南北广布+铁枝潮汕似皮"
     "影立体+驯猴搬箱写字绝活+国家级非遗以偶代人十指连心。"),
]

QUESTIONS = [
    ("QB-1798", "木偶戏有哪几大类？泉州提线木偶有什么绝活？",
     "传统文化", "技术直答",
     ["木偶戏", "提线木偶", "布袋戏", "泉州"], "通识拓展522·新卡"),
    ("QB-1799", "布袋木偶戏为什么又叫「掌中戏」？它流行在哪里？",
     "传统文化", "技术直答",
     ["布袋戏", "掌中木偶", "漳州", "泉州"], "通识拓展522·新卡"),
    ("QB-1800", "皮影戏的影人是用什么材料做的？怎么上色？",
     "传统文化", "技术直答",
     ["皮影", "牛皮", "驴皮", "雕刻"], "通识拓展522·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展522"],
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
    bank["version"] = "v7.87"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
