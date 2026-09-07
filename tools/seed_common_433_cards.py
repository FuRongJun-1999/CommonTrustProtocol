# -*- coding: utf-8 -*-
"""seed_common_433_cards.py · 通识拓展批次433知识卡+题库（幂等）

433：2 张存量卡补题（奥林匹克运动会 kp_card_olympics /
    篮球比赛基本规则 kp_card_basketball，均已在库）
    + 1 张新卡（射箭 kp_card_archery，题库卡库双零）。
体育赛事三连。预检已过（QB-1537~1539 可用，
奥运会起源/格言、篮球规则、射箭题库 0 覆盖）。
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
             "XMind", "HDR", "Robotaxi", "FIBA"}


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
    ("kp_card_archery",
     "射箭",
     "体育运动知识点内容（人话接口）", "体育常识",
     "射箭——静与准的奥运会项目：①**历史**——弓箭最初是狩猎与战争工具，"
     "近代转为竞技运动；1900 年起进入奥运会，1972 年慕尼黑奥运会起成为"
     "常设项目；②**奥运规则**——反曲弓项目距离 70 米：先打排位赛（72"
     " 支箭按总环数排名），再进入一对一淘汰对抗赛，环数高者胜；③**计"
     "分**——靶纸从中心向外 10 环到 1 环，箭越靠近靶心得分越高；④**"
     "技术要领**——站位、搭箭、开弓、瞄准、撒放五步，撒放瞬间的呼吸与"
     "心态控制是关键（「稳、准、匀」）；⑤**格局**——韩国队长期霸榜"
     "奥运射箭奖牌榜，中国队的反曲弓项目也具备夺牌实力。",
     ["射箭的规则", "奥运会射箭距离", "射箭怎么计分",
      "射箭的起源", "反曲弓是什么", "射箭技术要领"],
     ["问射击运动", "问飞镖"],
     "atomic", "",
     "射箭=弓箭狩猎战争工具转竞技1900入奥1972常设+反曲弓70米排位72箭"
     "一对一淘汰环数高者胜+靶纸10环到1环越近靶心越高+站位搭箭开弓瞄准"
     "撒放五步呼吸心态控制稳准匀+韩国长期霸榜中国有夺牌实力。"),
]

QUESTIONS = [
    ("QB-1537", "现代奥运会是什么时候复兴的？奥运格言是什么？",
     "体育常识", "技术直答",
     ["奥运会", "顾拜旦", "格言", "四年"], "通识拓展433·存量卡补题"),
    ("QB-1538", "篮球比赛每队上场几人？得分规则是什么？",
     "体育常识", "技术直答",
     ["篮球", "规则", "三分", "走步"], "通识拓展433·存量卡补题"),
    ("QB-1539", "奥运会射箭比赛的距离是多少？怎么计分？",
     "体育常识", "技术直答",
     ["射箭", "靶心", "计分", "奥运会"], "通识拓展433"),
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
                               "level:L2", "status:verified", "batch:通识拓展433"],
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
    bank["version"] = "v7.04"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
