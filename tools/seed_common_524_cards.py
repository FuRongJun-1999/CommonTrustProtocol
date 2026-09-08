# -*- coding: utf-8 -*-
"""seed_common_524_cards.py · 通识拓展批次524知识卡+题库（幂等）

524：1 张新卡 + 1 张存量卡补题·曲艺域
    （评书与曲艺 kp_card_ping 新卡——id 与语义等价卡名双重确认双零；
    相声补题挂 kp_card_crosstalk——与 QB-1395 说学逗唱题不重复）。
预检已过（QB-1804~1806 可用）。
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
    ("kp_card_ping",
     "评书与曲艺",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "评书与曲艺——一副嘴皮子的江湖：①**评书**——一人一桌一扇一醒木"
     "：定场诗开篇，「欲知后事如何，且听下回分解」的「扣子」（悬念）留"
     "人；说书人「跳进跳出」，一会儿叙事一会儿扮角色；②**传统书目**——"
     "《三国》《隋唐演义》《岳飞传》《三侠五义》；③**评书大家**——单田"
     "芳（沙哑嗓音独树一帜）、袁阔成（《三国演义》评书巅峰）、刘兰芳"
     "（《岳飞传》万人空巷）、田连元（电视评书开先河）；④**快板**——竹"
     "板打节拍、数来宝演变而来，李润杰创快板书，贯口一气呵成；⑤**京韵"
     "大鼓**——鼓曲代表，骆玉笙一曲《重整河山待后生》苍凉入骨；⑥**曲"
     "艺**——说唱艺术总称，与戏曲「扮上演出」不同，曲艺以「说唱叙述」"
     "为本。",
     ["评书是什么", "单田芳", "袁阔成", "刘兰芳岳飞传",
      "快板", "醒木"],
     ["问相声", "问京剧"],
     "atomic", "",
     "评书曲艺=一人一桌一扇一醒木定场诗开篇扣子留悬念跳进跳出+书目三国"
     "隋唐岳飞传三侠五义+大家单田芳袁阔成三国刘兰芳岳飞传田连元电视评"
     "书+快板竹板数来宝李润杰+京韵大鼓骆玉笙重整河山+曲艺说唱叙述为本"
     "。"),
]

QUESTIONS = [
    ("QB-1804", "评书的「三件道具」是什么？「扣子」指什么？",
     "传统文化", "技术直答",
     ["评书", "醒木", "折扇", "扣子"], "通识拓展524·新卡"),
    ("QB-1805", "相声演员为什么要论师承辈分？传统段子《关公战秦琼》讽刺什么？",
     "传统文化", "技术直答",
     ["相声", "师承", "关公战秦琼", "侯宝林"], "通识拓展524·存量补题"),
    ("QB-1806", "快板是什么艺术？京韵大鼓的代表人物是谁？",
     "传统文化", "技术直答",
     ["快板", "京韵大鼓", "骆玉笙", "数来宝"], "通识拓展524·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展524"],
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
    bank["version"] = "v7.89"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
