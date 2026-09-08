# -*- coding: utf-8 -*-
"""seed_common_532_cards.py · 通识拓展批次532知识卡+题库（幂等）

532：1 张新卡 + 1 张存量卡补题·礼俗度量域
    （度量衡 kp_card_duliangheng 新卡——id 与语义等价卡名双重确认无独立卡，
    「半斤八两」十六两制角度零覆盖；宴席座次补题挂 kp_card_seating，
    首测验证后缺口再补强；汉服 kp_card_hanfu2 已有卡跳过）。
预检已过（QB-1828~1830 可用）。
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
    ("kp_card_duliangheng",
     "度量衡",
     "制度史知识点内容（人话接口）", "历史与文明",
     "度量衡——古人怎么称量世界：①**三字分工**——「度」量长度（寸、"
     "尺、丈、里），「量」量容积（合、升、斗、斛），「衡」称重量（铢、"
     "两、斤、钧、石）；②**成语活化石**——「千钧一发」（钧=三十斤）、"
     "「半斤八两」（旧制一斤十六两，半斤恰是八两，彼此彼此）、「才高"
     "八斗」（谢灵运评曹植）；③**十六两一斤的传说**——老秤十六颗秤星"
     "=北斗七星+南斗六星+福禄寿三星，商贩短一两损福、短二两伤禄、短三"
     "两折寿——用信仰约束诚信；1959 年才改为十两一斤；④**秦统一度量"
     "衡**——公元前 221 年秦始皇统一全国度量衡，诏书铸在标准器「权」"
     "（砝码）上，「车同轨、书同文」配套工程；⑤**石**作重量单位读"
     " dàn，一石约合一百二十斤（汉代）。",
     ["度量衡是什么", "半斤八两", "千钧一发", "秦统一度量衡",
      "十六两一斤", "石怎么读"],
     ["问秦朝", "问古代货币"],
     "atomic", "",
     "度量衡=度量长度寸尺丈里量容积合升斗斛衡重量铢两斤钧石+千钧一发"
     "钧三十斤半斤八两旧制十六两一斤+十六星北斗七南斗六福禄寿三缺一两"
     "损福短二两伤禄三两折寿诚信约束1959改十两+秦前221统一度量衡诏书"
     "铸权砝码+石读dàn汉代约120斤。"),
]

QUESTIONS = [
    ("QB-1828", "度量衡的「度」「量」「衡」分别指什么？",
     "历史常识", "技术直答",
     ["度量衡", "长度", "容积", "重量"], "通识拓展532·新卡"),
    ("QB-1829", "「半斤八两」是怎么来的？旧制一斤为什么是十六两？",
     "历史常识", "技术直答",
     ["半斤八两", "十六两", "秤星", "诚信"], "通识拓展532·新卡"),
    ("QB-1830", "中国宴席上的座次怎么安排？哪里是上座？",
     "传统文化", "技术直答",
     ["座次", "上座", "宴席", "礼仪"], "通识拓展532·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展532"],
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
    bank["version"] = "v7.97"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
