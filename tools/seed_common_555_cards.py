# -*- coding: utf-8 -*-
"""seed_common_555_cards.py · 通识拓展批次555知识卡+题库（幂等）

555：1 张新卡·三国典故域（三国演义经典桥段 kp_card_sanguo——
    id 与语义等价卡名双重确认；桃园结义 QB-1333 已有，
    赤壁/草船借箭/三顾茅庐典故角度零覆盖故立）。
预检已过（QB-1897~1899 可用）。
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
    ("kp_card_sanguo",
     "三国演义经典桥段",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "三国演义经典桥段——智与勇的名场面：①**赤壁之战**——建安十三年"
     "（208 年）孙刘联军以火攻大破曹操，黄盖诈降纵火定乾坤；演义里诸"
     "葛亮「借东风」、草船借箭（雾中受箭交差）皆为艺术加工；②**三顾茅"
     "庐**——刘备三次亲赴隆中请诸葛亮出山，《隆中对》预判三分天下；"
     "③**空城计**——马谡失街亭后，诸葛亮大开城门焚香操琴吓退司马懿，"
     "史无此事、小说妙笔；④**忠义谱**——桃园结义、千里走单骑、单刀赴"
     "会、白帝城托孤；⑤**意义**——「七分实三分虚」的历史演义范式，"
     "塑造了中国人对智谋文化的集体想象。",
     ["赤壁之战", "草船借箭", "三顾茅庐", "空城计",
      "借东风", "隆中对"],
     ["问桃园三结义", "问三国历史"],
     "atomic", "",
     "三国桥段=赤壁208孙刘联军火攻黄盖诈降借东风草船借箭演义加工+三顾"
     "茅庐隆中对三分天下+空城计操琴吓退司马懿史无此事小说妙笔+桃园结义"
     "千里走单骑白帝托孤忠义谱+七分实三分虚历史演义范式智谋文化集体想"
     "象。"),
]

QUESTIONS = [
    ("QB-1897", "赤壁之战是谁和谁打的？「草船借箭」是怎么回事？",
     "历史常识", "技术直答",
     ["赤壁之战", "草船借箭", "诸葛亮", "火攻"], "通识拓展555·新卡"),
    ("QB-1898", "「三顾茅庐」讲的是什么？《隆中对》说了什么？",
     "历史常识", "技术直答",
     ["三顾茅庐", "刘备", "隆中对", "三分天下"], "通识拓展555·新卡"),
    ("QB-1899", "「空城计」是真实的吗？司马懿为什么退兵？",
     "历史常识", "技术直答",
     ["空城计", "诸葛亮", "司马懿", "演义"], "通识拓展555·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展555"],
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
    bank["version"] = "v8.20"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
