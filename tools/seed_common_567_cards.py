# -*- coding: utf-8 -*-
"""seed_common_567_cards.py · 通识拓展批次567知识卡+题库（幂等）

567：2 张新卡·琴瓷雅物域（古琴减字谱 kp_card_jianzipu /
    瓷枕 kp_card_cizhen——id 与语义等价卡名双重确认双零）。
预检已过（QB-1933~1935 可用）。
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
    ("kp_card_jianzipu",
     "古琴减字谱",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "古琴减字谱——把音乐写成「天书」的智慧：①**最早琴谱**——南朝梁"
     "丘明传谱的《碣石调·幽兰》，唐代手抄本今藏日本，是现存最早的琴曲"
     "谱（逐句文字记录的「文字谱」）；②**减字谱**——唐人曹柔在文字谱"
     "基础上创制：把指法、弦序、徽位拼成一个个「减字」符号，一字一音"
     "位，惜墨如金；③**不记节奏**——减字谱只记指法音位不严格记节奏，"
     "后人「打谱」还原需依琴家理解，故同一曲各家弹法不同——打谱是二次"
     "创作；④**《神奇秘谱》**——明初朱权编（1425 年），现存最早的减字"
     "谱琴曲集，收录《广陵散》《高山》《流水》等；⑤**意义**——三千年"
     "琴曲靠它流传至今，是活着的音乐文物。",
     ["减字谱", "碣石调幽兰", "曹柔", "神奇秘谱",
      "打谱", "古琴谱"],
     ["问古琴", "问十二平均律"],
     "atomic", "",
     "减字谱=碣石调幽兰南朝梁丘明唐代手抄文字谱现存最早藏日本+唐曹柔创"
     "减字谱指法弦序徽位拼减字一字一音位+不严记节奏打谱二次创作各家弹法"
     "不同+神奇秘谱1425朱权现存最早减字谱集广陵散高山流水+三千年琴曲流"
     "传活的音乐文物。"),
    ("kp_card_cizhen",
     "瓷枕",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "瓷枕——硬邦邦的清凉夏梦：①**源流**——隋代出现，唐宋金元鼎盛，"
     "是古人夏日消暑的「空调枕」；②**名品**——北宋定窑白瓷「孩儿枕」"
     "（故宫博物院藏，童子伏卧为枕，传世名器）；磁州窑白地黑花瓷枕多题"
     "诗句与人物故事；③**诗意**——李清照「玉枕纱厨，半夜凉初透」中的"
     "玉枕即夏日瓷枕一类；④**讲究**——瓷枕硬而凉，古人认为「久枕瓷枕"
     "，明目益睛」，枕面或刻或画皆成文章；⑤**演变**——明清软枕普及后"
     "瓷枕渐退为陈设与随葬器。",
     ["瓷枕", "孩儿枕", "定窑", "磁州窑",
      "玉枕纱厨", "消夏"],
     ["问五大名窑", "问明式家具"],
     "atomic", "",
     "瓷枕=隋代出现唐宋金元鼎盛夏日空调枕+定窑白瓷孩儿枕故宫传世名器+"
     "磁州窑白地黑花题诗人物+李清照玉枕纱厨半夜凉初透+硬而凉明目益睛之"
     "说明清软枕普及退为陈设。"),
]

QUESTIONS = [
    ("QB-1933", "什么是古琴「减字谱」？它是谁创制的？",
     "传统文化", "技术直答",
     ["减字谱", "曹柔", "古琴", "指法"], "通识拓展567·新卡"),
    ("QB-1934", "现存最早的琴曲谱是什么？为什么说「打谱」是二次创作？",
     "传统文化", "技术直答",
     ["碣石调幽兰", "打谱", "文字谱", "琴曲"], "通识拓展567·新卡"),
    ("QB-1935", "北宋定窑「孩儿枕」是什么？瓷枕有什么用处？",
     "传统文化", "技术直答",
     ["孩儿枕", "定窑", "瓷枕", "消暑"], "通识拓展567·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展567"],
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
    bank["version"] = "v8.32"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
