# -*- coding: utf-8 -*-
"""seed_common_395_cards.py · 通识拓展批次395知识卡+题库（幂等）

395：2 张存量卡补题（萤火虫发光 kp_card_fireflyglow /
    蚯蚓与土壤改良 kp_card_earthworm，均已在库）
    + 1 张新卡（企鹅 kp_card_penguin，题库卡库双零）。
KCCS 四要素+题干原句触发词。预检已过（QB-1423~1425 可用）。
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
             "MTBF", "SQA"}


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
    ("kp_card_penguin",
     "企鹅",
     "动物常识知识点内容（人话接口）", "自然与生物",
     "企鹅——不会飞的游泳鸟类：①**住在哪**——几乎所有企鹅都生活在"
     "南半球（南极沿岸最集中）；**北极没有企鹅**（北大西洋曾有的大海雀"
     "外形酷似企鹅，19 世纪被人类捕杀灭绝）；②**为什么不会飞**——翅膀"
     "演化成短平的「鳍状肢」，在水中划水像飞行一样敏捷（时速可达十几"
     "公里），是「用翅膀游泳」的鸟；③**抗寒装备**——厚脂肪层+层层"
     "重叠的防水羽毛，双层保暖；帝企鹅在南极冬天冰面上孵蛋——雄企鹅"
     "把蛋放在脚背上用腹部皮褶盖住，站着孵化约两个月、期间不吃东西；"
     "④**天敌**——水中是海豹和虎鲸，岸上贼鸥偷蛋和雏鸟；⑤**辨析**——"
     "企鹅是鸟（有羽毛、卵生），不是哺乳动物。",
     ["企鹅生活在南极还是北极", "企鹅会飞吗", "帝企鹅怎么孵蛋",
      "企鹅为什么不怕冷", "北极有企鹅吗", "企鹅是哺乳动物吗"],
     ["问北极熊", "问海鸟"],
     "atomic", "",
     "企鹅=南半球南极为主北极没有企鹅（大海雀灭绝）+翅膀演化鳍状肢水"
     "中游泳像飞行+脂肪层防水羽毛双层保暖+帝企鹅雄性脚背孵蛋两个月绝"
     "食+天敌海豹虎鲸贼鸥+是鸟不是哺乳动物。"),
]

QUESTIONS = [
    ("QB-1423", "萤火虫为什么会发光？这种光有什么特别之处？",
     "自然与生物", "技术直答",
     ["萤火虫", "发光", "冷光", "求偶"], "通识拓展395·存量卡补题"),
    ("QB-1424", "蚯蚓对土壤有什么好处？雨后为什么会爬到地面上？",
     "自然与生物", "技术直答",
     ["蚯蚓", "土壤", "呼吸", "松土"], "通识拓展395·存量卡补题"),
    ("QB-1425", "企鹅生活在南极还是北极？企鹅会飞吗？",
     "自然与生物", "技术直答",
     ["企鹅", "南极", "北极", "飞"], "通识拓展395"),
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
                               "level:L2", "status:verified", "batch:通识拓展395"],
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
    bank["version"] = "v6.65"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
