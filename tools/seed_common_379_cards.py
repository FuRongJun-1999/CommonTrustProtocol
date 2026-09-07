# -*- coding: utf-8 -*-
"""seed_common_379_cards.py · 通识拓展批次379知识卡+题库（幂等）

379：2 张存量卡补题（生活垃圾分类/天干地支与十二生肖）
    + 1 张新卡（毛笔与文房四宝 kp_card_brush，卡库无同名卡）。
KCCS 四要素+题干原句触发词。预检已过（QB-1375~1377 可用，
垃圾分类/生肖题库 0 覆盖，毛笔卡库题库双零）。
（本批次号曾被困倦睡眠重复题占用，2026-09-07 重写为真实新题。）
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("kp_card_brush",
     "毛笔与文房四宝",
     "传统文化知识点内容（人话接口）", "传统文化",
     "毛笔——中国传统书写绘画工具：①**文房四宝**——笔、墨、纸、砚，"
     "代表上品为湖笔（浙江湖州）、徽墨（安徽徽州）、宣纸（安徽宣城）、"
     "端砚（广东肇庆）；②**按笔毫分类**——狼毫（黄鼠狼尾毛，硬而有"
     "弹性，适合勾线）、羊毫（山羊毛，软而蓄墨多，适合晕染铺写）、"
     "兼毫（二者混合，软硬适中，初学者常用）；③**好笔四德**——尖"
     "（锋颖聚拢尖锐）、齐（润开后笔锋铺齐）、圆（笔头饱满圆润）、健"
     "（按压后弹性恢复好）；④**使用保养**——新笔温水发开，用后洗净"
     "悬挂晾干（笔杆朝下防胶水积根）；⑤**关联**——书法五体（篆隶楷"
     "行草）都以毛笔为载体，「笔法」是中国书画的核心语言。",
     ["文房四宝是什么", "毛笔有哪些种类", "狼毫羊毫区别",
      "怎么挑毛笔", "兼毫是什么", "毛笔怎么保养"],
     ["问墨", "问宣纸"],
     "atomic", "",
     "毛笔=文房四宝笔墨纸砚湖笔徽墨宣纸端砚+狼毫硬弹羊毫软蓄墨兼毫适"
     "中初学常用+好笔四德尖齐圆健+新笔温水发开用后洗净悬挂晾干+书法篆"
     "隶楷行草五体以毛笔为载体。"),
]

QUESTIONS = [
    ("QB-1375", "生活垃圾分哪四大类？剩饭剩菜和废电池分别属于什么垃圾？",
     "环保常识", "技术直答",
     ["垃圾分类", "厨余", "有害", "可回收"], "通识拓展379·存量卡补题"),
    ("QB-1376", "十二生肖的顺序是什么？天干地支纪年是怎么回事？",
     "传统文化", "技术直答",
     ["生肖", "顺序", "天干地支", "纪年"], "通识拓展379·存量卡补题"),
    ("QB-1377", "文房四宝指的是什么？毛笔按笔毫怎么分类？",
     "传统文化", "技术直答",
     ["文房四宝", "毛笔", "狼毫", "羊毫"], "通识拓展379"),
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
                               "level:L2", "status:verified", "batch:通识拓展379"],
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
    bank["version"] = "v6.49"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
