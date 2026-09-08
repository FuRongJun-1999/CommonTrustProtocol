# -*- coding: utf-8 -*-
"""seed_common_525_cards.py · 通识拓展批次525知识卡+题库（幂等）

525：1 张新卡·地方戏曲域（地方戏大观 kp_card_xiqu_map——豫剧/评剧/
    粤剧与经典剧目角度；黄梅戏 kp_card_huangmei2、昆曲 kp_card_kunqu2
    已有卡跳过；越剧地方特色 QB-1283 已覆盖，本批补剧目角度）。
预检已过（QB-1807~1809 可用）。
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
    ("kp_card_xiqu_map",
     "地方戏大观",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "地方戏大观——一方水土一方腔：①**豫剧**——河南梆子，唱腔高亢豪"
     "迈，常香玉《花木兰》一句「谁说女子不如男」家喻户晓（抗美援朝期"
     "间她义演捐飞机，「香玉剧社号」）；②**评剧**——发源于河北唐山一"
     "带、盛行于京津东北，唱词通俗生活气足，新凤霞《刘巧儿》《花为媒》"
     "代表，赵丽蓉也是评剧出身；③**越剧**——浙江嵊州，中国第二大剧"
     "种，全女班起家长于才子佳人，《梁山伯与祝英台》《红楼梦》凄美缠绵"
     "，《梁祝》被誉「东方的罗密欧与朱丽叶」；④**粤剧**——广东，广府"
     "白话演唱，红线女「红腔」名动省港澳，周恩来誉之「南国红豆」，2009"
     " 年入选人类非遗；⑤**黄梅戏、昆曲**——黄梅采茶调起家《天仙配》"
     "、昆曲「百戏之祖」均有专卡。",
     ["豫剧是哪里戏", "花木兰谁说女子不如男", "常香玉",
      "评剧", "新凤霞刘巧儿", "越剧梁祝", "粤剧南国红豆"],
     ["问黄梅戏", "问昆曲"],
     "atomic", "",
     "地方戏大观=豫剧河南梆子常香玉花木兰谁说女子不如男义演捐香玉剧社"
     "号飞机+评剧河北唐山京津东北新凤霞刘巧儿花为媒赵丽蓉评剧出身+越"
     "剧浙江嵊州第二大剧种全女班梁祝红楼梦东方罗密欧朱丽叶+粤剧红线女"
     "红腔南国红豆2009人类非遗+黄梅戏昆曲见专卡。"),
]

QUESTIONS = [
    ("QB-1807", "豫剧《花木兰》「谁说女子不如男」是谁唱红的？",
     "传统文化", "技术直答",
     ["豫剧", "花木兰", "常香玉", "谁说女子不如男"], "通识拓展525·新卡"),
    ("QB-1808", "越剧《梁山伯与祝英台》讲了什么？为什么被誉东方罗密欧与朱丽叶？",
     "传统文化", "技术直答",
     ["越剧", "梁祝", "化蝶", "爱情"], "通识拓展525·新卡"),
    ("QB-1809", "评剧《刘巧儿》的主演是谁？评剧流行在哪些地区？",
     "传统文化", "技术直答",
     ["评剧", "新凤霞", "刘巧儿", "唐山"], "通识拓展525·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展525"],
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
    bank["version"] = "v7.90"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
