# -*- coding: utf-8 -*-
"""seed_common_577_cards.py · 通识拓展批次577知识卡+题库（幂等）

577：1 张新卡·琉璃料器域（琉璃与料器 kp_card_liuli——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1963~1965 可用）。
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
    ("kp_card_liuli",
     "琉璃与料器",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "琉璃与料器——火里炼出的彩色玻璃：①**琉璃**——中国古代玻璃的"
     "称呼，西周已有琉璃珠；战国「蜻蜓眼」玻璃珠受西方工艺影响，蓝绿"
     "圈纹如蜻蜓复眼；②**建筑琉璃**——琉璃瓦与琉璃构件用于宫殿庙坛，"
     "黄色琉璃唯皇家可用，等级森严；北京门头沟琉璃渠村是明清皇家琉璃"
     "官窑，琉璃烧制技艺列入国家级非遗；③**料器**——北京料器：无模"
     "自由吹制的低温玻璃工艺品，一杆铁签一团火，「灯工」手艺；山东博"
     "山（颜神镇）是明清琉璃重镇，《颜山杂记》专记琉璃工艺；④**琉璃厂"
     "**——北京文化街因明清烧琉璃得名，后成书肆文物集散地；⑤**意趣**"
     "——火中取色，一件料器小动物要趁热一气呵成。",
     ["琉璃", "料器", "蜻蜓眼", "琉璃瓦",
      "琉璃厂", "博山琉璃"],
     ["问五大名窑", "问景泰蓝"],
     "atomic", "",
     "琉璃料器=中国古代玻璃称呼西周琉璃珠战国蜻蜓眼+建筑琉璃瓦黄色唯"
     "皇家门头沟琉璃渠官窑非遗+料器北京无模灯工博山颜神镇颜山杂记+琉璃"
     "厂因烧琉璃得名后成书肆文物街+火中取色一气呵成。"),
]

QUESTIONS = [
    ("QB-1963", "古代的「琉璃」是什么？「蜻蜓眼」是什么珠子？",
     "传统文化", "技术直答",
     ["琉璃", "蜻蜓眼", "玻璃", "战国"], "通识拓展577·新卡"),
    ("QB-1964", "建筑琉璃瓦为什么是等级的象征？",
     "传统文化", "技术直答",
     ["琉璃瓦", "等级", "皇家", "黄色"], "通识拓展577·新卡"),
    ("QB-1965", "「料器」是什么工艺？琉璃厂的名字怎么来的？",
     "传统文化", "技术直答",
     ["料器", "灯工", "琉璃厂", "北京"], "通识拓展577·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展577"],
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
    bank["version"] = "v8.42"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
