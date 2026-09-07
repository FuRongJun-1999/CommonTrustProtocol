# -*- coding: utf-8 -*-
"""seed_common_375_cards.py · 通识拓展批次375知识卡+题库（幂等）

375：3 张存量卡补题（蜜蜂舞蹈语言/奥运五环/欧盟欧元区申根区）
    + 1 张新卡（中国象棋 kp_card_chess，题库卡库双零）。
KCCS 四要素+题干原句触发词。预检已过（QB-1362~1365 可用）。
（本批次号曾被困倦睡眠重复题占用，2026-09-07 重写为真实新题。）
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO"}


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
    ("kp_card_chess",
     "中国象棋",
     "传统棋类知识点内容（人话接口）", "传统文化",
     "中国象棋——两人对弈的棋盘游戏，源于楚汉相争的象征：①**棋盘**——"
     "9 条竖线 × 10 条横线，中间「楚河汉界」分隔双方，棋子放在交叉点上"
     "（不同于围棋；国际象棋放格子里）；②**棋子**——双方各 16 子：将/帅"
     "各 1、士/仕各 2、象/相各 2、马各 2、车各 2、炮各 2、兵/卒各 5；"
     "③**走法口诀**——马走日、象走田、车走直路炮翻山、士走斜线护将边、"
     "小卒一去不回还（过河前只能前进，过河后可左右）；④**胜负规则**——"
     "将死对方的将/帅即胜；另有规则「将帅不能照面」（同一竖线上中间无"
     "棋子时隔空相对，走出的一方判负）；⑤**和棋**——双方无子可动或"
     "重复局面不变可判和。",
     ["中国象棋规则", "象棋马走日象走田", "将帅不能照面",
      "象棋有几个棋子", "楚河汉界是什么", "象棋怎么算赢"],
     ["问围棋规则", "问国际象棋"],
     "atomic", "",
     "中国象棋=9×10棋盘楚河汉界双方各16子将士象马车炮兵+马走日象走田"
     "车走直路炮翻山士走斜线卒过河可横移+将死对方将帅获胜+将帅不能照面"
     "（同竖线无阻隔走出方判负）+棋子放交叉点。"),
]

QUESTIONS = [
    ("QB-1362", "蜜蜂为什么要跳舞？8字舞是什么意思？",
     "自然与生物", "技术直答",
     ["蜜蜂", "跳舞", "8字舞", "蜜源"], "通识拓展375·存量卡补题"),
    ("QB-1363", "奥运五环的五个颜色分别代表什么？",
     "体育常识", "技术直答",
     ["五环", "颜色", "五大洲", "顾拜旦"], "通识拓展375·存量卡补题"),
    ("QB-1364", "欧盟、欧元区和申根区有什么区别？",
     "世界常识", "技术直答",
     ["欧盟", "欧元区", "申根", "区别"], "通识拓展375·存量卡补题"),
    ("QB-1365", "中国象棋有哪些棋子？将帅不能照面是什么规则？",
     "传统文化", "技术直答",
     ["象棋", "棋子", "将帅", "照面"], "通识拓展375"),
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
                               "level:L2", "status:verified", "batch:通识拓展375"],
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
    bank["version"] = "v6.45"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
