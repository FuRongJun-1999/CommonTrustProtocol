# -*- coding: utf-8 -*-
"""seed_common_539_cards.py · 通识拓展批次539知识卡+题库（幂等）

539：2 张新卡·文玩雅玩域（文玩核桃 kp_card_hetao /
    鼻烟壶 kp_card_binyanhu——id 与语义等价卡名双重确认双零）。
预检已过（QB-1849~1851 可用）。
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
    ("kp_card_hetao",
     "文玩核桃",
     "民俗雅玩知识点内容（人话接口）", "传统文化",
     "文玩核桃——掌中盘出包浆玉化：①**是什么**——野生麻核桃经过长年"
     "把玩揉搓成为文玩，讲究品类纹路：狮子头、虎头、官帽、公子帽、鸡心"
     "等，狮子头最受推崇；②**「盘」**——上手揉搓谓之盘，汗手润泽、"
     "日久包浆红润如玛瑙玉化，急不得；③**配对**——两只核桃纹路、大小、"
     "形制要高度一致，天然核桃配对率极低，「千里难寻一对」；④**名品**"
     "——四座楼狮子头、磨盘狮子头等以产地树名闻名；⑤**风习**——清代"
     "宫廷王府流行，「贝勒手中三件宝：扳指、核桃、笼中鸟」，盘核桃至今"
     "是街头一景。",
     ["文玩核桃", "盘核桃", "狮子头", "配对",
      "包浆", "贝勒手中三件宝"],
     ["问玉文化", "问鼻烟壶"],
     "atomic", "",
     "文玩核桃=麻核桃野生把玩文玩狮子头虎头官帽公子帽鸡心狮子头最尊+盘"
     "上手揉搓汗手润泽包浆红润玉化急不得+配对纹路大小一致千里难寻一对+"
     "四座楼磨盘产地树名+清代贝勒三件宝扳指核桃笼中鸟街头一景。"),
    ("kp_card_binyanhu",
     "鼻烟壶",
     "民俗雅玩知识点内容（人话接口）", "传统文化",
     "鼻烟壶——方寸之间的乾坤：①**鼻烟**——明末由利玛窦等传教士带入"
     "中国的舶来品，吸闻提神，清代上流社会人人鼻烟壶不离身；②**器小艺"
     "大**——鼻烟壶通常掌心大小，材质有玻璃（料器）、瓷、玉、漆、玛"
     "瑙等；③**内画绝技**——以内壁磨砂的玻璃壶为纸，特制弯头细笔伸入"
     "小口「反手」作画——正面看反面画，山水人物纤毫毕现，方寸之间见天"
     "地；④**四大流派**——京派、冀派（衡水王习三为代表）、鲁派（博山"
     "）、粤派（汕头）；衡水内画 2006 年列入国家级非物质文化遗产；⑤**"
     "收藏**——清代内画名家壶已成拍场珍品。",
     ["鼻烟壶", "内画", "王习三", "鼻烟壶四大流派",
      "衡水内画", "利玛窦鼻烟"],
     ["问文玩核桃", "问珐琅"],
     "atomic", "",
     "鼻烟壶=鼻烟明末利玛窦带入吸闻提神清代上流不离身+掌心大小料器瓷"
     "玉漆玛瑙+内画壶内壁磨砂弯头细笔反手作画正面看反面画方寸见天地+四"
     "大流派京冀鲁粤衡水王习三2006国家级非遗+清代名家壶拍场珍品。"),
]

QUESTIONS = [
    ("QB-1849", "「盘核桃」是怎么盘的？文玩核桃讲究什么？",
     "传统文化", "技术直答",
     ["盘核桃", "文玩核桃", "狮子头", "包浆"], "通识拓展539·新卡"),
    ("QB-1850", "文玩核桃为什么讲究「配对」？什么核桃最名贵？",
     "传统文化", "技术直答",
     ["配对", "狮子头", "四座楼", "纹路"], "通识拓展539·新卡"),
    ("QB-1851", "鼻烟壶内画是怎么画出来的？有哪些流派？",
     "传统文化", "技术直答",
     ["内画", "鼻烟壶", "反手作画", "衡水"], "通识拓展539·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展539"],
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
    bank["version"] = "v8.04"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
