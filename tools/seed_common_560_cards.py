# -*- coding: utf-8 -*-
"""seed_common_560_cards.py · 通识拓展批次560知识卡+题库（幂等）

560：1 张新卡·八仙传说域（八仙过海 kp_card_baxian——
    id 与语义等价卡名双重确认双零；四大发明已有双卡跳过）。
预检已过（QB-1912~1914 可用）。
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
    ("kp_card_baxian",
     "八仙过海",
     "神话传说知识点内容（人话接口）", "传统文化",
     "八仙过海——各显神通的仙人天团：①**八仙是谁**——铁拐李（拄铁拐"
     "背葫芦）、汉钟离（手摇棕扇袒腹）、张果老（倒骑毛驴抱渔鼓）、吕洞"
     "宾（背纯阳剑）、何仙姑（执荷花，唯一女仙）、蓝采和（提花篮）、韩"
     "湘子（吹笛箫）、曹国舅（持玉板，皇后之弟）；②**八仙过海**——赴"
     "蟠桃会归途过东海，相约不驾云、各凭法宝渡海：铁拐李踏葫芦、何仙姑"
     "浮荷花、张果老倒骑驴踏水……遂有「八仙过海，各显神通」——比喻各"
     "凭本事竞争；③**吕洞宾典故**——「狗咬吕洞宾，不识好人心」（苟杳"
     "故事谐音）、三醉岳阳楼、黄粱一梦由钟离权点化；④**影响**——八仙"
     "形象常见于年画、瓷器、戏曲，是民间最亲近的仙人组合。",
     ["八仙过海", "八仙有哪八位", "吕洞宾", "各显神通",
      "张果老", "何仙姑"],
     ["问封神演义", "问牛郎织女"],
     "atomic", "",
     "八仙过海=铁拐李葫芦汉钟离棕扇张果老倒骑毛驴渔鼓吕洞宾纯阳剑何仙"
     "姑荷花蓝采和花篮韩湘子笛箫曹国舅玉板+过东海不驾云各凭法宝渡海各"
     "显神通比喻各凭本事+狗咬吕洞宾苟杳谐音三醉岳阳楼黄粱一梦+年画瓷"
     "器戏曲民间最亲近仙人组合。"),
]

QUESTIONS = [
    ("QB-1912", "「八仙过海，各显神通」说的是什么？八仙有哪几位？",
     "传统文化", "技术直答",
     ["八仙过海", "各显神通", "八仙", "法宝"], "通识拓展560·新卡"),
    ("QB-1913", "「狗咬吕洞宾」的典故是怎么来的？吕洞宾是谁？",
     "传统文化", "技术直答",
     ["吕洞宾", "狗咬吕洞宾", "苟杳", "纯阳剑"], "通识拓展560·新卡"),
    ("QB-1914", "张果老为什么倒骑毛驴？何仙姑是八仙里的谁？",
     "传统文化", "技术直答",
     ["张果老", "倒骑毛驴", "何仙姑", "荷花"], "通识拓展560·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展560"],
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
    bank["version"] = "v8.25"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
