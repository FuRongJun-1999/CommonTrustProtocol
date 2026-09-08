# -*- coding: utf-8 -*-
"""seed_common_542_cards.py · 通识拓展批次542知识卡+题库（幂等）

542：2 张新卡·书香旧藏域（善本收藏 kp_card_shanben /
    连环画收藏 kp_card_lianhuanhua——id 与语义等价卡名双重确认双零）。
预检已过（QB-1858~1860 可用）。
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
    ("kp_card_shanben",
     "善本收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "善本收藏——书中的黄金屋：①**什么是善本**——校勘精审、流传稀少"
     "、时代久远的珍贵版本（张之洞概括为足本、精本、旧本三义）；②**「"
     "一页宋版，一两黄金」**——宋元刻本存世稀少，历来是藏书家心头好；"
     "③**藏书家**——清乾嘉黄丕烈自号「佞宋主人」，藏宋版百余种名其斋"
     "「百宋一廛」；乾隆善本专库「天禄琳琅」为皇家藏书精华；④**鉴定要"
     "点**——看纸墨刀法、避讳字与刻工年代、递藏印章（名家藏书印加分"
     "）；⑤**保护**——防潮防蛀防光，拿书必净手，晒书亦有度。",
     ["善本", "宋版", "一页宋版一两黄金", "黄丕烈",
      "天禄琳琅", "藏书印"],
     ["问古籍装帧", "问集邮"],
     "atomic", "",
     "善本收藏=校勘精审流传稀少时代久远张之洞足本精本旧本三义+一页宋版"
     "一两黄金宋元刻本稀珍+黄丕烈佞宋主人百宋一廛天禄琳琅乾隆专库+鉴定"
     "纸墨刀法避讳字刻工年代递藏印+防潮防蛀净手晒书有度。"),
    ("kp_card_lianhuanhua",
     "连环画收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "连环画收藏——小人书里的大时代：①**是什么**——连环画俗称「小人"
     "书」，图文并茂讲述故事，20 世纪上海兴起，新中国成立后成为大众读"
     "物主力；②**名家名作**——贺友直《山乡巨变》（白描大师）、王叔晖"
     "《西厢记》（工笔重彩）、刘继卣《大闹天宫》；③**黄金年代**——上"
     "世纪七八十代发行量动辄百万册，八十年代后期式微；④**收藏热**——"
     "九十年代末起旧连环画翻红，藏家自称「连友」，初版、名家绘画、品相"
     "全否决定身价；⑤**意义**——一代人的美术启蒙与时代记忆。",
     ["连环画", "小人书", "贺友直", "王叔晖",
      "山乡巨变", "连友"],
     ["问善本收藏", "问集邮"],
     "atomic", "",
     "连环画收藏=小人书20世纪上海兴起新中国大众读物主力+贺友直山乡巨变"
     "白描王叔晖西厢记工笔刘继卣大闹天宫+七八十代百万册黄金年代后式微+"
     "连友收藏初版名家品相定身价+一代人美术启蒙时代记忆。"),
]

QUESTIONS = [
    ("QB-1858", "什么是「善本」？为什么说「一页宋版一两黄金」？",
     "传统文化", "技术直答",
     ["善本", "宋版", "藏书", "校勘"], "通识拓展542·新卡"),
    ("QB-1859", "清代大藏书家黄丕烈有什么雅号和藏书故事？",
     "历史常识", "技术直答",
     ["黄丕烈", "佞宋主人", "百宋一廛", "藏书家"], "通识拓展542·新卡"),
    ("QB-1860", "连环画（小人书）的经典作品和画家有哪些？",
     "传统文化", "技术直答",
     ["连环画", "小人书", "贺友直", "王叔晖"], "通识拓展542·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展542"],
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
    bank["version"] = "v8.07"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
