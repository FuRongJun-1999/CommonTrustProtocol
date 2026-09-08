# -*- coding: utf-8 -*-
"""seed_common_582_cards.py · 通识拓展批次582知识卡+题库（幂等）

582：2 张新卡·食文化域（豆腐 kp_card_doufu /
    满汉全席 kp_card_manhan——id 与语义等价卡名双重确认双零；
    八大菜系/饺子/火锅已有卡查重跳过）。
预检已过（QB-1978~1980 可用）。
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
    ("kp_card_doufu",
     "豆腐",
     "饮食文化知识点内容（人话接口）", "传统文化",
     "豆腐——「植物肉」的中国发明：①**起源传说**——相传汉代淮南王刘"
     "安炼丹偶得，两千余年历史（史学界另有考辨，传统说法通行）；②**点"
     "卤成豆腐**——豆浆煮沸后加盐卤（氯化镁）或石膏（硫酸钙）使蛋白质"
     "凝固，故有「卤水点豆腐，一物降一物」；③**家族谱系**——豆腐脑/豆"
     "花（未压型）、水豆腐、豆腐干、冻豆腐、千张百叶、油豆腐，发酵的腐"
     "乳与臭豆腐风味独树；④**营养**——蛋白丰富易吸收，被誉为「植物肉"
     "」；⑤**传播**——唐代随禅宗东传日本，今已走向世界餐桌。",
     ["豆腐是谁发明的", "刘安", "卤水点豆腐", "豆腐脑",
      "臭豆腐", "植物肉"],
     ["问豆浆", "问满汉全席"],
     "atomic", "",
     "豆腐=相传汉代淮南王刘安炼丹偶得两千年历史+卤水点豆腐一物降一物盐"
     "卤石膏凝固蛋白+豆腐脑豆花未压型豆腐干冻豆腐千张油豆腐腐乳臭豆腐"
     "发酵风味+蛋白丰富植物肉+唐代随禅宗传日本走向世界。"),
    ("kp_card_manhan",
     "满汉全席",
     "饮食文化知识点内容（人话接口）", "传统文化",
     "满汉全席——清代宴席的天花板：①**由来**——清宫与官场宴席中满席"
     "与汉席合流而成，乾隆年间大兴；②**规模**——通常说一百零八品，南"
     "菜五十四、北菜五十四，需数日方能食毕；③**集大成**——满族烧烤点"
     "心与传统汉菜烹饪技法合璧，山珍海错穷极水陆；④**礼制**——入席次"
     "序、上菜章法、奏乐行酒皆有规制，是宴饮礼仪的集大成；⑤**如今**——"
     "完整复原极难，今多为取其名的改良宴席，其文化意义大于实用。",
     ["满汉全席", "一百零八品", "清代宴席", "满席汉席",
      "山珍海错", "宴饮礼仪"],
     ["问豆腐", "问八大菜系"],
     "atomic", "",
     "满汉全席=清宫官场满席汉席合流乾隆年间大兴+通常108品南54北54数日"
     "食毕+满族烧烤点心汉菜烹饪技法合璧山珍海错+入席上菜奏乐行酒规制集"
     "大成+完整复原极难今多改良宴文化意义大于实用。"),
]

QUESTIONS = [
    ("QB-1978", "豆腐相传是谁发明的？「卤水点豆腐」是什么原理？",
     "传统文化", "技术直答",
     ["豆腐", "刘安", "卤水", "点豆腐"], "通识拓展582·新卡"),
    ("QB-1979", "豆腐有哪些「家族成员」？臭豆腐是怎么做的？",
     "传统文化", "技术直答",
     ["豆腐脑", "臭豆腐", "腐乳", "冻豆腐"], "通识拓展582·新卡"),
    ("QB-1980", "满汉全席有多少道菜？它是怎么形成的？",
     "传统文化", "技术直答",
     ["满汉全席", "108品", "清代宴席", "合璧"], "通识拓展582·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展582"],
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
    bank["version"] = "v8.47"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
