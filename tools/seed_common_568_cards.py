# -*- coding: utf-8 -*-
"""seed_common_568_cards.py · 通识拓展批次568知识卡+题库（幂等）

568：1 张新卡·匏器鸣虫域（匏器与蝈蝈葫芦 kp_card_paoqi——
    id 与语义等价卡名双重确认双零；招幌葫芦/悬壶角度 QB-1795
    已覆盖，本批立范制工艺角度不重复）。
预检已过（QB-1936~1938 可用）。
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
    ("kp_card_paoqi",
     "匏器与鸣虫文化",
     "民俗雅玩知识点内容（人话接口）", "传统文化",
     "匏器与鸣虫文化——葫芦长出来的器物与虫趣：①**匏器（范制葫芦）**"
     "——把幼葫芦套进刻花木模/瓦范，随果实生长长出所需造型与纹饰，出"
     "模后加工，清代康熙宫廷范匏最盛（笔筒、瓶、盒皆成御用器）；②**蝈"
     "蝈葫芦**——冬日怀揣听鸣虫：葫芦口配玳瑁象牙镂雕「蒙心」，内有铜"
     "丝簧护虫，虫鸣经葫芦共鸣格外清亮；③**斗蟋蟀（促织）**——斗虫之"
     "风起于唐盛于宋，南宋贾似道著《促织经》是世界第一部蟋蟀专著；蒲"
     "松龄《促织》一篇讽刺进贡之害，入选课本；山东宁阳产名虫；④**玩"
     "法讲究**——「本长」天然长成的葫芦最贵，配蒙心、配虫皆有行家眼"
     "光；⑤**意趣**——一虫一葫芦，冬日怀中鸣声不断，是老北京的冬"
     "日雅趣。",
     ["匏器", "范制葫芦", "蝈蝈葫芦", "斗蟋蟀",
      "促织", "蒙心"],
     ["问文玩核桃", "问泥人与面塑"],
     "atomic", "",
     "匏器鸣虫=匏器范制葫芦幼果套模随长成形纹饰清代康熙宫廷御用笔筒瓶"
     "盒+蝈蝈葫芦冬日怀揣蒙心玳瑁象牙镂雕铜丝簧共鸣清亮+斗蟋蟀促织唐起"
     "宋盛贾似道促织经世界第一部专著蒲松龄促织讽刺宁阳名虫+本长葫芦最"
     "贵行家眼光+冬日怀中鸣声老北京雅趣。"),
]

QUESTIONS = [
    ("QB-1936", "匏器是什么？葫芦怎么「长」成器物？",
     "传统文化", "技术直答",
     ["匏器", "范制葫芦", "模具", "宫廷"], "通识拓展568·新卡"),
    ("QB-1937", "蝈蝈葫芦有什么讲究？冬天为什么要怀揣葫芦？",
     "传统文化", "技术直答",
     ["蝈蝈葫芦", "蒙心", "鸣虫", "冬日"], "通识拓展568·新卡"),
    ("QB-1938", "斗蟋蟀（促织）之风起源于何时？《促织经》是谁写的？",
     "传统文化", "技术直答",
     ["斗蟋蟀", "促织", "贾似道", "促织经"], "通识拓展568·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展568"],
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
    bank["version"] = "v8.33"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
