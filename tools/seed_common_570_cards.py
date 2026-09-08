# -*- coding: utf-8 -*-
"""seed_common_570_cards.py · 通识拓展批次570知识卡+题库（幂等）

570：1 张新卡·扇子文化域（扇子文化 kp_card_shanzi——
    id 与语义等价卡名双重确认无独立卡；眼镜 QB-620/783
    已有题覆盖跳过）。
预检已过（QB-1942~1944 可用）。
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
    ("kp_card_shanzi",
     "扇子文化",
     "传统文化知识点内容（人话接口）", "传统文化",
     "扇子文化——摇出来的风雅：①**团扇**——西汉班婕妤《怨歌行》以合"
     "欢扇自喻「弃捐箧笥中」，秋扇见捐成为失宠的经典意象；②**羽扇**"
     "——「羽扇纶巾」出自苏轼《念奴娇·赤壁怀古》，原形容周瑜谈笑退敌"
     "（常被误记为诸葛亮），后世演义才给孔明配上羽扇；③**折扇**——宋"
     "代由日本、高丽传入，明代大盛，扇面书画成为文人的流动画廊；④**蒲"
     "扇**——蒲葵扇是最平民的凉友，「轻摇蒲扇话家常」；⑤**《桃花扇》"
     "——清孔尚任传奇：侯方域与李香君，血溅诗扇点染成桃花，借离合之情"
     "写兴亡之感。",
     ["扇子文化", "团扇", "羽扇纶巾", "折扇",
      "桃花扇", "班婕妤"],
     ["问四大名扇", "问红楼梦"],
     "atomic", "",
     "扇子文化=团扇班婕妤怨歌行秋扇见捐宫怨意象+羽扇纶巾苏轼词原形容"
     "周瑜非诸葛亮演义才配羽扇+折扇宋代传入明代大盛书画流动画廊+蒲扇平"
     "民凉友+桃花扇孔尚任李香君血溅诗扇借离合写兴亡。"),
]

QUESTIONS = [
    ("QB-1942", "「秋扇见捐」的典故是什么？和哪位西汉才女有关？",
     "文学常识", "技术直答",
     ["团扇", "班婕妤", "怨歌行", "秋扇见捐"], "通识拓展570·新卡"),
    ("QB-1943", "「羽扇纶巾」在苏轼词里形容的是谁？",
     "文学常识", "技术直答",
     ["羽扇纶巾", "苏轼", "周瑜", "赤壁怀古"], "通识拓展570·新卡"),
    ("QB-1944", "《桃花扇》讲的是什么故事？「借离合之情写兴亡之感」怎么理解？",
     "文学常识", "技术直答",
     ["桃花扇", "孔尚任", "侯方域", "李香君"], "通识拓展570·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展570"],
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
    bank["version"] = "v8.35"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
