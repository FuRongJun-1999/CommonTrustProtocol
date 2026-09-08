# -*- coding: utf-8 -*-
"""seed_common_584_cards.py · 通识拓展批次584知识卡+题库（幂等）

584：1 张新卡·字谜歇后语域（字谜与歇后语 kp_card_zimi_xiehouyu——
    id 与语义等价卡名双重确认双零；灯谜已有庙会卡覆盖跳过）。
预检已过（QB-1984~1986 可用）。
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
    ("kp_card_zimi_xiehouyu",
     "字谜与歇后语",
     "民俗语言知识点内容（人话接口）", "传统文化",
     "字谜与歇后语——拆解与幽默的汉语智慧：①**字谜**——利用汉字可拆"
     "合的特性造谜：「一口咬掉牛尾巴」打一字（告）、「半个月亮」打一字"
     "（胖：月+半）；②**离合传统**——字谜源于汉代离合体，拆字合字"
     "是文人酒令与灯谜的常客；③**歇后语**——前半是比方、后半是解释，"
     "两截式幽默：外甥打灯笼——照舅（旧）、小葱拌豆腐——一清二白、"
     "泥菩萨过江——自身难保、哑巴吃黄连——有苦说不出、韩信点兵——多"
     "多益善、芝麻开花——节节高；④**共性**——都吃透汉字一字多义、谐"
     "音双关的特性，是汉语独有的语言游戏。",
     ["字谜", "一口咬掉牛尾巴", "歇后语", "外甥打灯笼",
      "韩信点兵", "芝麻开花"],
     ["问灯谜", "问汉字六书"],
     "atomic", "",
     "字谜歇后语=汉字拆合特性一口咬掉牛尾巴告半个月亮胖+离合体汉代起文"
     "人酒令灯谜常客+歇后语前比后解外甥打灯笼照舅小葱拌豆腐一清二白泥"
     "菩萨过江自身难保哑巴吃黄连韩信点兵多多益善芝麻开花节节高+一字多"
     "义谐音双关汉语独有游戏。"),
]

QUESTIONS = [
    ("QB-1984", "「一口咬掉牛尾巴」打一字，谜底是什么？",
     "传统文化", "技术直答",
     ["字谜", "告", "拆字", "一口咬掉牛尾巴"], "通识拓展584·新卡"),
    ("QB-1985", "「外甥打灯笼」的歇后语下一句是什么？",
     "传统文化", "技术直答",
     ["外甥打灯笼", "照舅", "照旧", "歇后语"], "通识拓展584·新卡"),
    ("QB-1986", "「小葱拌豆腐」和「韩信点兵」的歇后语各是什么？",
     "传统文化", "技术直答",
     ["小葱拌豆腐", "一清二白", "韩信点兵", "多多益善"], "通识拓展584·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展584"],
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
    bank["version"] = "v8.49"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
