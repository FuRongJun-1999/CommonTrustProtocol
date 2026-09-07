# -*- coding: utf-8 -*-
"""seed_common_517_cards.py · 通识拓展批次517知识卡+题库（幂等）

517：1 张新卡 + 1 张存量卡补题·经济文学域
    （漕运与盐政 kp_card_caoyun 新卡——id 与语义等价卡名双重确认双零；
    阿Q正传补题挂鲁迅卡 kp_card_luxun——与 QB-1551 不重复；
    敦煌文书因 QB-1565 藏经洞已覆盖跳过）。
预检已过（QB-1783~1785 可用）。
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
    ("kp_card_caoyun",
     "漕运与盐政",
     "经济史知识点内容（人话接口）", "历史与文明",
     "漕运与盐政——古代王朝的两大经济命脉：①**漕运**——把南方产粮区"
     "的漕粮经水路运往京师与边镇的体系，隋唐大运河、京杭大运河都为它"
     "而生；清代岁运漕粮约四百万石；②**漕运管理**——明清设漕运总督"
     "（驻江苏淮安，「运河之都」），沿线设粮仓（如唐代含嘉仓、回洛仓）"
     "，行船者结成漕帮；1901 年清末改海运与铁路，漕运废止；③**盐政**"
     "——盐税长期是国家第二大税源；汉武帝时桑弘羊推行盐铁官营开专卖"
     "先河，后世演变为「盐引」制度——商人凭引购盐、划区运销（引岸专"
     "商）；④**扬州盐商**——明清两淮盐利甲天下，扬州盐商富可敌国，"
     "修园林、养戏班，成就扬州繁华；⑤**改革**——道光年间陶澍改行票盐"
     "制，打破垄断。",
     ["漕运是什么", "漕运总督", "盐铁专卖", "盐引制度",
      "扬州盐商", "古代税收"],
     ["问京杭大运河", "问都江堰"],
     "atomic", "",
     "漕运盐政=漕粮南粮北运水路体系运河而生清代岁约四百万石+漕运总督"
     "驻淮安运河之都含嘉仓回洛仓1901年废改海运铁路+盐税第二大税源汉武"
     "帝桑弘羊盐铁官营盐引引岸专商+扬州盐商富甲园林+陶澍票盐制破垄断"
     "。"),
]

QUESTIONS = [
    ("QB-1783", "什么是漕运？明清的漕运总督驻在哪个城市？",
     "历史常识", "技术直答",
     ["漕运", "漕粮", "淮安", "运河"], "通识拓展517·新卡"),
    ("QB-1784", "盐铁专卖是从哪个皇帝时期开始的？盐引制度怎么运作？",
     "历史常识", "技术直答",
     ["盐铁专卖", "汉武帝", "桑弘羊", "盐引"], "通识拓展517·新卡"),
    ("QB-1785", "阿Q正传的「精神胜利法」是什么？鲁迅借此批判了什么？",
     "文学常识", "技术直答",
     ["阿Q正传", "精神胜利法", "国民性", "鲁迅"], "通识拓展517·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展517"],
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
    bank["version"] = "v7.82"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
