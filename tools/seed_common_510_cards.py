# -*- coding: utf-8 -*-
"""seed_common_510_cards.py · 通识拓展批次510知识卡+题库（幂等）

510：2 张新卡·文教域（四大书院 kp_card_shuyuan / 汉字六书
    kp_card_liushu——按卡名精确确认无独立卡；科举 QB-897/1516 已覆盖跳过；
    六书总括题与 QB-1120/1485 单点题共存不冲突）。
预检已过（QB-1762~1764 可用）。
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
    ("kp_card_shuyuan",
     "四大书院",
     "文教历史知识点内容（人话接口）", "历史与文明",
     "中国古代四大书院——宋代书院教育的巅峰：①**岳麓书院**——湖南长"
     "沙岳麓山下（今湖南大学内），大门联「惟楚有材，于斯为盛」，朱熹"
     "与张栻曾在此「朱张会讲」；②**白鹿洞书院**——江西庐山五老峰下"
     "，朱熹重建并制定《白鹿洞书院揭示》，成为中国书院学规典范；③**"
     "嵩阳书院**——河南登封嵩山南麓，程颢、程颐、司马光曾在此讲学"
     "，「程门立雪」故事即发生在理学讲学背景下；④**应天府书院**——"
     "河南商丘，范仲淹曾在此就读并执教；⑤**意义**——书院是古代私人"
     "或官府聚徒讲学的机构，藏书、讲学、祭祀三合一，与科举互补，是理"
     "学传播与学术自由讨论的重镇。",
     ["四大书院是哪四个", "岳麓书院", "白鹿洞书院", "嵩阳书院",
      "程门立雪", "书院是干什么的"],
     ["问科举制度", "问孔子"],
     "atomic", "",
     "四大书院=岳麓书院长沙惟楚有材于斯为盛朱张会讲+白鹿洞书院庐山朱"
     "熹白鹿洞书院揭示学规典范+嵩阳书院登封二程司马光讲学程门立雪背"
     "景+应天府书院商丘范仲淹就读执教+书院藏书讲学祭祀三合一理学重"
     "镇。"),
    ("kp_card_liushu",
     "汉字六书",
     "文字学知识点内容（人话接口）", "历史与文明",
     "汉字六书——古人总结的造字用字方法（许慎《说文解字》）：①**象"
     "形**——画成其物：日、月、山、水；②**指事**——用抽象符号示意："
     "上、下、本（木下加点指根部）、刃（刀口加点）；③**会意**——合"
     "两字见新意：明（日+月）、休（人+木）、武（止+戈）；④**形声**——"
     "形旁表义+声旁表音：江、河、湖、晴，汉字八成以上是形声字；⑤**转"
     "注**——同部首互训的字：考、老互相解释；⑥**假借**——借同音字表"
     "示新义：自（本指鼻子）借为自己、莫（本指日落）借为否定词；⑦**"
     "要点**——前四者是造字法，后两者是用字法；汉字演变主线：甲骨文"
     "→金文→篆→隶→楷。",
     ["汉字六书是什么", "象形字和指事字区别", "形声字",
      "会意字举例", "说文解字", "许慎"],
     ["问甲骨文", "问仓颉造字"],
     "atomic", "",
     "六书=许慎说文解字总结+象形日月山水画成其物+指事上下本刃抽象符"
     "号+会意明休武合字见新意+形声江河形旁表义声旁表音八成以上+转注"
     "考老互训+假借自莫借同音+前四造字后二用字+甲骨文金文篆隶楷演变"
     "。"),
]

QUESTIONS = [
    ("QB-1762", "中国古代四大书院是哪四个？分布在哪些地方？",
     "历史常识", "技术直答",
     ["四大书院", "岳麓", "白鹿洞", "嵩阳"], "通识拓展510·新卡"),
    ("QB-1763", "汉字的六书指什么？形声字为什么占大多数？",
     "文化常识", "技术直答",
     ["六书", "象形", "指事", "形声"], "通识拓展510·新卡"),
    ("QB-1764", "「程门立雪」讲的是谁的故事？发生在哪个书院背景下？",
     "历史常识", "技术直答",
     ["程门立雪", "程颢", "程颐", "嵩阳书院"], "通识拓展510·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展510"],
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
    bank["version"] = "v7.75"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
