# -*- coding: utf-8 -*-
"""seed_common_528_cards.py · 通识拓展批次528知识卡+题库（幂等）

528：1 张新卡·漆器域（漆器与螺钿 kp_card_qiqi——id 与语义等价卡名
    双重确认双零；青花瓷 kp_card_blueporc2、斗拱榫卯 kp_card_dougong2
    已有卡查重跳过）。
预检已过（QB-1816~1818 可用）。
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
    ("kp_card_qiqi",
     "漆器与螺钿",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "漆器与螺钿——大漆里泡出来的东方美学：①**大漆**——天然生漆从漆"
     "树割取，「百里千刀一斤漆」，生漆致敏俗称「咬人」，漆匠的手都是"
     "熬出来的；②**源流**——河姆渡遗址朱漆木碗距今约七千年，战国曾"
     "侯乙墓漆器华美，汉代马王堆云纹漆器上书「君幸食」「君幸酒」——"
     "两千年前的宴请用语；③**螺钿**——把贝壳磨成薄片嵌入漆面，光照"
     "下虹彩流转，唐代大盛（日本正仓院藏唐代螺钿紫檀五弦琵琶是孤品）；"
     "④**雕漆（剔红）**——漆一层层堆到几十层再雕刻红花纹，朱红厚重；"
     "⑤**名产地**——福州脱胎漆器（轻若浮云）、扬州漆器、成都漆器；"
     "⑥**地位**——大漆防腐耐酸千年不坏，是先于瓷器的「国民涂料」。",
     ["漆器是什么", "大漆", "螺钿", "剔红", "脱胎漆器",
      "君幸食"],
     ["问五大名窑", "问青花瓷"],
     "atomic", "",
     "漆器螺钿=生漆百里千刀一斤漆致敏咬人+河姆渡朱漆木碗七千年曾侯乙"
     "马王堆君幸食君幸酒+螺钿贝片镶嵌虹光唐代大盛正仓院五弦琵琶+剔红"
     "堆漆雕刻+福州脱胎扬州成都名产+防腐耐酸千年不坏先于瓷器的国民涂"
     "料。"),
]

QUESTIONS = [
    ("QB-1816", "中国的漆器有多久历史？「君幸食」是什么意思？",
     "传统文化", "技术直答",
     ["漆器", "河姆渡", "马王堆", "君幸食"], "通识拓展528·新卡"),
    ("QB-1817", "螺钿工艺是什么？用的是什么材料？",
     "传统文化", "技术直答",
     ["螺钿", "贝壳", "镶嵌", "漆器"], "通识拓展528·新卡"),
    ("QB-1818", "「百里千刀一斤漆」说的是什么？大漆为什么珍贵？",
     "传统文化", "技术直答",
     ["大漆", "生漆", "漆树", "割漆"], "通识拓展528·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展528"],
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
    bank["version"] = "v7.93"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
