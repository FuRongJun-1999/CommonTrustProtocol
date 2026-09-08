# -*- coding: utf-8 -*-
"""seed_common_589_cards.py · 通识拓展批次589知识卡+题库（幂等）

589：1 张新卡·扇藏雅玩域（扇面与扇骨收藏 kp_card_shangu_wenhua——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1999~2001 可用）。
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
    ("kp_card_shangu_wenhua",
     "扇面与扇骨收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "扇面与扇骨收藏——怀袖雅物的收藏门道：①**怀袖雅物**——折扇的"
     "美称：开合自如、随身入怀，是旧时文人的袖中清玩；②**扇面收藏**——"
     "明清名家扇面书画自成门类：一扇有画有书、一面字一面画，方寸藏气"
     "韵；③**扇骨收藏**——材质论：湘妃竹（斑如泪痕）最雅、乌木象牙"
     "贵重；工艺论：留青、浮雕、镶嵌各有手法；④**名坊**——杭州王星记"
     "扇庄（1875 年创）至今制扇；⑤**保存**——书画扇怕潮怕晒，宜常"
     "展挂、忌久折，配扇袋扇匣养护。",
     ["扇面收藏", "扇骨", "湘妃竹", "怀袖雅物",
      "王星记", "成扇"],
     ["问四大名扇", "问扇子文化"],
     "atomic", "",
     "扇面扇骨收藏=折扇美称怀袖雅物随身清玩+明清名家扇面书画一面字一"
     "面画方寸藏气韵+扇骨湘妃竹泪斑最雅乌木象牙贵重留青浮雕镶嵌+杭州王"
     "星记1875扇庄+书画扇怕潮怕晒常展挂扇袋扇匣养护。"),
]

QUESTIONS = [
    ("QB-1999", "折扇为什么被称为「怀袖雅物」？",
     "传统文化", "技术直答",
     ["怀袖雅物", "折扇", "文人", "清玩"], "通识拓展589·新卡"),
    ("QB-2000", "湘妃竹扇骨为什么名贵？斑纹有什么传说？",
     "传统文化", "技术直答",
     ["湘妃竹", "斑竹", "泪斑", "扇骨"], "通识拓展589·新卡"),
    ("QB-2001", "收藏书画扇要注意什么？成扇和扇面哪个更难保存？",
     "传统文化", "技术直答",
     ["成扇", "扇面", "保存", "防潮"], "通识拓展589·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展589"],
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
    bank["version"] = "v8.54"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
