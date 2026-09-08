# -*- coding: utf-8 -*-
"""seed_common_537_cards.py · 通识拓展批次537知识卡+题库（幂等）

537：1 张新卡·家具工艺域（明式家具 kp_card_mingjiaju——
    id 与语义等价卡名双重确认双零；石窟造像卡已多覆盖佛像题材故跳过）。
预检已过（QB-1843~1845 可用）。
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
    ("kp_card_mingjiaju",
     "明式家具",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "明式家具——不用一根钉子的东方设计巅峰：①**用材**——黄花梨（海"
     "南黄花梨纹理如鬼脸最珍）、紫檀、鸡翅木等硬木，木性稳定纹理天成；"
     "②**结构**——全靠榫卯接合，不用铁钉少用胶，拆装自如可传数百年；"
     "③**风格**——线条简练流畅、比例匀称、不加繁饰，后世概括为「简、"
     "厚、精、雅」；④**代表器型**——圈椅（靠背圆弧如环，暗合「天圆"
     "地方」）、太师椅（唯一以官职命名的椅子）、官帽椅、翘头案、架子"
     "床；⑤**流派**——苏作（江南精巧）、广作（广州华丽重雕）、京作"
     "（宫廷气派）；⑥**研究**——王世襄《明式家具珍赏》1985 年出版，"
     "把明式家具推上世界设计圣坛，至今是各国设计师的灵感源泉。",
     ["明式家具", "圈椅", "太师椅", "榫卯", "黄花梨",
      "王世襄"],
     ["问斗拱榫卯", "问瓷器"],
     "atomic", "",
     "明式家具=黄花梨紫檀鸡翅木硬木纹理天成+榫卯接合不用铁钉可传数百"
     "年+简厚精雅线条简练不加繁饰+圈椅天圆地方太师椅唯一官职命名官帽"
     "椅翘头案架子床+苏作广作京作三流派+王世襄明式家具珍赏1985推上世"
     "界设计圣坛。"),
]

QUESTIONS = [
    ("QB-1843", "明式家具有什么风格特点？为什么不用一根钉子？",
     "传统文化", "技术直答",
     ["明式家具", "榫卯", "黄花梨", "风格"], "通识拓展537·新卡"),
    ("QB-1844", "圈椅的造型有什么讲究？太师椅的名字怎么来的？",
     "传统文化", "技术直答",
     ["圈椅", "太师椅", "官帽椅", "造型"], "通识拓展537·新卡"),
    ("QB-1845", "明式家具主要用什么木材？有哪几大流派？",
     "传统文化", "技术直答",
     ["黄花梨", "紫檀", "苏作", "广作"], "通识拓展537·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展537"],
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
    bank["version"] = "v8.02"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
