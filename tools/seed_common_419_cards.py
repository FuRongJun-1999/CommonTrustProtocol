# -*- coding: utf-8 -*-
"""seed_common_419_cards.py · 通识拓展批次419知识卡+题库（幂等）

419：2 张存量卡补题（蜗牛与软体动物·章鱼角度 kp_card_snail /
    仿生学 kp_card_bionics，均已在库）
    + 1 张新卡（水母 kp_card_jellyfish，题库卡库双零）。
KCCS 四要素+题干原句触发词。预检已过（QB-1495~1497 可用；
蝙蝠回声定位已有 QB-929 排除回声卡）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("kp_card_jellyfish",
     "水母",
     "海洋生物知识点内容（人话接口）", "自然与生物",
     "水母——海洋里的「透明精灵」：①**身体构造**——95% 以上是水，没有"
     "大脑、心脏、血液和骨骼，只有一张简单的神经网——却已在地球上存在"
     "了 6 亿多年，比恐龙古老得多；②**怎么行动与捕食**——靠伞状体收缩"
     "喷水推进；触手上的刺细胞（刺丝囊）会在接触瞬间弹出注射毒素，麻痹"
     "小鱼小虾；③**被水母蜇了怎么办**——先用海水冲洗（淡水会让刺细胞"
     "继续放电，越冲越糟！），小心清除残留触手，严重时立即就医；用尿液"
     "冲洗是误区；④**奇闻**——灯塔水母理论上能「返老还童」：从成体"
     "退回幼体阶段重新生长，近乎无限循环；⑤**发光**——部分水母体内有"
     "荧光蛋白，在深海发出幽幽冷光。",
     ["水母为什么透明", "水母有毒吗", "被水母蜇了怎么办",
      "灯塔水母不死", "水母有大脑吗", "水母发光"],
     ["问珊瑚", "问深海生物"],
     "atomic", "",
     "水母=95%以上是水无大脑心脏血液骨骼只有神经网已存在6亿年+伞状体"
     "喷水推进触手刺细胞注毒捕食+蜇伤用海水冲洗淡水加重放电清触手就医"
     "尿液是误区+灯塔水母返老还童退回幼体近乎无限循环+部分有荧光蛋白"
     "深海发光。"),
]

QUESTIONS = [
    ("QB-1495", "章鱼是软体动物吗？蜗牛和章鱼有什么关系？",
     "自然与生物", "技术直答",
     ["章鱼", "软体动物", "蜗牛", "头足"], "通识拓展419·存量卡补题"),
    ("QB-1496", "什么是仿生学？雷达和魔术贴分别模仿了什么？",
     "科学技术", "技术直答",
     ["仿生学", "雷达", "魔术贴", "模仿"], "通识拓展419·存量卡补题"),
    ("QB-1497", "水母为什么几乎透明？被水母蜇了应该怎么处理？",
     "自然与生物", "技术直答",
     ["水母", "透明", "蜇伤", "刺细胞"], "通识拓展419"),
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
                               "level:L2", "status:verified", "batch:通识拓展419"],
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
    bank["version"] = "v6.90"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
