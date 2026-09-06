# -*- coding: utf-8 -*-
"""seed_common_348_cards.py · 通识拓展批次348知识卡+题库（幂等）

348：文化-越剧/文化-黄梅戏（地方戏曲新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1283/1284+双id可用）。
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
             "BCS", "B2H6", " borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_yueju2",
     "越剧",
     "戏曲艺术知识点内容（人话接口）", "文化",
     "越剧——中国第二大剧种：①**发源**——浙江嵊州（1906 年落地唱书演变为"
     "戏，早期全男班）；②**女子越剧**——20 世纪 20-30 年代女班兴起，"
     "「女子越剧」成为独特标志（女小生反串是特色美学）；③**风格**——"
     "唱腔委婉柔美（尹派/徐派/傅派/袁派等流派），长于抒情才子佳人题材；"
     "④**代表剧目**——《梁山伯与祝英台》（走向世界的东方"
     "《罗密欧与朱丽叶》）/《红楼梦》（徐玉兰王文娟的宝黛）/《祥林嫂》；"
     "⑤**新艺术改革**——1940 年代袁雪芬倡导新越剧（编导制/立体布景/"
     "吸收话剧电影手法）；⑥**现状**——浙江/上海主力院团传承，《梁山伯"
     "与祝英台》1953 年拍成新中国第一部彩色戏曲电影。",
     ["越剧是哪里的剧种", "越剧的特点", "梁山伯与祝英台越剧",
      "女子越剧", "越剧流派", "红楼梦越剧"],
     ["问越剧名家", "问其他地方戏"],
     "atomic", "",
     "越剧=1906浙江嵊州落地唱书演变第二大剧种+女子越剧女小生反串独特"
     "美学+唱腔委婉柔美尹徐傅袁流派+梁祝红楼梦祥林嫂代表作+袁雪芬"
     "新越剧改革编导制立体布景+1953梁祝新中国首部彩色戏曲电影。"),
    ("kp_card_huangmei2",
     "黄梅戏",
     "戏曲艺术知识点内容（人话接口）", "文化",
     "黄梅戏——泥土芬芳的民歌戏：①**发源**——源于湖北黄梅采茶调，"
     "壮大于安徽安庆（严凤英使其名扬全国）；②**风格**——唱腔淳朴流畅"
     "（明快抒情），表演质朴细致，通俗易懂生活气息浓（「表演"
     "贴近生活」）；③**代表剧目**——《天仙配》（七仙女下嫁董永「夫妻"
     "双双把家还」家喻户晓）/《女驸马》（「为救李郎离家园」冯素珍女扮"
     "男装中状元）；④**名家**——严凤英（七仙女/冯素贞塑造者，黄梅戏"
     "一代宗师）、王少舫；⑤**特点**——唱词口语化念白近安庆方言，小"
     "生小旦小丑「三小戏」见长，比京剧昆曲更接近民歌；⑥**地位**——"
     "全国五大剧种之一（京剧/越剧/黄梅戏/评剧/豫剧）。",
     ["黄梅戏是哪里的", "黄梅戏的特点", "天仙配",
      "女驸马", "严凤英", "夫妻双双把家还"],
     ["问采茶戏", "问地方戏对比"],
     "atomic", "",
     "黄梅戏=源于湖北黄梅采茶调壮大安徽安庆+唱腔淳朴流畅表演质朴生活"
     "气息浓+天仙配七仙女董永夫妻双双把家还+女驸马冯素珍女扮男装中状元"
     "+严凤英一代宗师+全国五大剧种之一。"),
]

QUESTIONS = [
    ("QB-1283", "越剧是哪个地方的剧种？有什么特色？", "文化", "技术直答",
     ["越剧", "浙江", "女小生", "梁山伯"], "通识拓展348"),
    ("QB-1284", "黄梅戏发源于哪里？《天仙配》讲的是什么故事？", "文化", "技术直答",
     ["黄梅戏", "湖北", "天仙配", "七仙女"], "通识拓展348"),
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
                               "level:L2", "status:verified", "batch:通识拓展348"],
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
    bank["version"] = "v6.14"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
