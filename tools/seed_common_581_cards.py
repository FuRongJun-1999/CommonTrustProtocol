# -*- coding: utf-8 -*-
"""seed_common_581_cards.py · 通识拓展批次581知识卡+题库（幂等）

581：1 张新卡·四立食俗域（立春立夏立秋立冬食俗 kp_card_silishisu——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1975~1977 可用）。
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
    ("kp_card_silishisu",
     "四立食俗",
     "民俗知识点内容（人话接口）", "传统文化",
     "四立食俗——跟着节气吃的仪式感：①**立春咬春**——立春日吃春饼"
     "（「咬春」）、嚼萝卜迎新，俗语「咬得草根断，则百事可做」；②**立"
     "夏挂蛋**——立夏吃蛋挂蛋络防「疰夏」（夏日困乏），还有立夏称人"
     "记体重的旧俗；③**立秋贴秋膘**——苦夏掉膘，立秋吃肉把膘「贴」回"
     "来；④**立冬补冬**——「立冬补冬，补嘴空」：北方吃饺子（交子之"
     "时），南方炖鸡鸭姜母鸭；⑤**逻辑**——四立是四季起点，以「吃」"
     "应时令既是营养补充也是仪式感，把日子过出节气味。",
     ["立春咬春", "立夏蛋", "立秋贴秋膘", "立冬补冬",
      "春饼", "疰夏"],
     ["问二十四节气", "问数九与三伏"],
     "atomic", "",
     "四立食俗=立春咬春吃春饼嚼萝卜咬得草根断百事可做+立夏吃蛋挂蛋络防"
     "疰夏称人记体重+立秋贴秋膘苦夏掉膘吃肉补回+立冬补冬补嘴空北方饺子"
     "南方姜母鸭交子之时+四立四季起点以吃应时令仪式感节气味。"),
]

QUESTIONS = [
    ("QB-1975", "立春「咬春」要吃什么？有什么寓意？",
     "传统文化", "技术直答",
     ["咬春", "春饼", "立春", "萝卜"], "通识拓展581·新卡"),
    ("QB-1976", "立夏为什么要吃蛋、挂蛋络？",
     "传统文化", "技术直答",
     ["立夏蛋", "疰夏", "挂蛋络", "称人"], "通识拓展581·新卡"),
    ("QB-1977", "「立冬补冬，补嘴空」是什么习俗？南北怎么吃？",
     "传统文化", "技术直答",
     ["立冬", "补冬", "饺子", "姜母鸭"], "通识拓展581·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展581"],
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
    bank["version"] = "v8.46"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
