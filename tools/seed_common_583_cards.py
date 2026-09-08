# -*- coding: utf-8 -*-
"""seed_common_583_cards.py · 通识拓展批次583知识卡+题库（幂等）

583：1 张新卡·联墨趣域（对联格律与趣联 kp_card_duilian_geru——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1981~1983 可用）。
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
    ("kp_card_duilian_geru",
     "对联格律与趣联",
     "传统文化知识点内容（人话接口）", "传统文化",
     "对联格律与趣联——文字对仗的游戏规则：①**格律四要**——字数相"
     "等、词性相对（名对名、动对动）、平仄相谐（上联收仄、下联收平）、"
     "内容相关；大忌「合掌」（上下联意思重复）；②**趣联故事**——解缙"
     "「门对千竿竹，家藏万卷书」：对方砍竹、挖根，他随即续「短」「无」"
     "化解，机敏传为佳话；③**回文联**——「客上天然居，居然天上客」"
     "（纪晓岚对「人过大佛寺，寺佛大过人」），倒读顺读皆成文；④**数字"
     "联**——卓文君《怨郎诗》以一至十、百千万数字串起相思；⑤**无情"
     "对**——字字工对而意思毫不相干，是文字游戏的极致。",
     ["对联格律", "平仄", "合掌", "回文联",
      "解缙", "无情对"],
     ["问汉字六书", "问书法"],
     "atomic", "",
     "对联趣联=格律四要字数相等词性相对平仄相谐上仄下平内容相关忌合掌+"
     "解缙门对千竿竹家藏万卷书续短无机敏+回文联客上天然居居然天上客纪"
     "晓岚大佛寺+怨郎诗一至十数字串相思+无情对字工对意不相干文字游戏极"
     "致。"),
]

QUESTIONS = [
    ("QB-1981", "对联的格律有哪几条基本要求？什么是「合掌」？",
     "传统文化", "技术直答",
     ["对联格律", "平仄", "词性", "合掌"], "通识拓展583·新卡"),
    ("QB-1982", "「客上天然居，居然天上客」是什么联？",
     "传统文化", "技术直答",
     ["回文联", "天然居", "纪晓岚", "倒读"], "通识拓展583·新卡"),
    ("QB-1983", "解缙「门对千竿竹」的趣联故事是怎样的？",
     "文学常识", "技术直答",
     ["解缙", "门对千竿竹", "家藏万卷书", "趣联"], "通识拓展583·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展583"],
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
    bank["version"] = "v8.48"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
