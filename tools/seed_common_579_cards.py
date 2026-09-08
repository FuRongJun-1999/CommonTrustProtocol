# -*- coding: utf-8 -*-
"""seed_common_579_cards.py · 通识拓展批次579知识卡+题库（幂等）

579：1 张新卡·近世服饰域（马褂与长衫 kp_card_magua——
    id 与语义等价卡名双重确认双零；旗袍 kp_card_qipao2
    已有专卡查重跳过）。
预检已过（QB-1969~1971 可用）。
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
    ("kp_card_magua",
     "马褂与长衫",
     "近世服饰知识点内容（人话接口）", "传统文化",
     "马褂与长衫——近世男装的两件套：①**马褂**——罩在长袍外的对襟短"
     "褂：有对襟、大襟、琵琶襟诸式；**黄马褂**是皇帝特赐的殊荣（侍卫"
     "服制、行围赏赐、功勋特赐三种来由）；②**长衫（长袍）**——士人日"
     "常正装，「长衫」与劳动者「短打」之分是旧时阶级标识——鲁迅笔下孔"
     "乙己是咸亨酒店「站着喝酒而穿长衫的唯一的人」；③**瓜皮帽**——六"
     "瓣缝合的便帽，取「六合统一」之意；④**中山装**——民国出现：四袋"
     "喻礼义廉耻、五扣喻五权分立（流行说法），是新式国家服装的代表；"
     "⑤**变迁**——长袍马褂→中山装→西装，衣冠之变即时代之变。",
     ["马褂", "黄马褂", "长衫", "孔乙己长衫",
      "瓜皮帽", "中山装"],
     ["问清代官服等级", "问旗袍"],
     "atomic", "",
     "马褂长衫=马褂对襟大襟琵琶襟罩袍外+黄马褂帝赐殊荣侍卫行围功勋+长"
     "衫士人正装与短打分阶级孔乙己站着喝酒穿长衫唯一人+瓜皮帽六瓣六合"
     "统一+中山装四袋礼义廉耻五扣五权流行说法+衣冠之变即时代之变。"),
]

QUESTIONS = [
    ("QB-1969", "黄马褂是什么？为什么它是殊荣？",
     "历史常识", "技术直答",
     ["黄马褂", "御赐", "殊荣", "清代"], "通识拓展579·新卡"),
    ("QB-1970", "孔乙己「穿长衫站着喝酒」说明了什么？",
     "文学常识", "技术直答",
     ["孔乙己", "长衫", "鲁迅", "阶级"], "通识拓展579·新卡"),
    ("QB-1971", "中山装的设计有什么寓意？",
     "传统文化", "技术直答",
     ["中山装", "四袋", "礼义廉耻", "设计"], "通识拓展579·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展579"],
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
    bank["version"] = "v8.44"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
