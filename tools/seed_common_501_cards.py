# -*- coding: utf-8 -*-
"""seed_common_501_cards.py · 通识拓展批次501知识卡+题库（幂等）

501：1 张新卡 + 1 张存量卡补题·棋类规则域
    （国际象棋规则 kp_card_intlchess 新卡——按卡名精确确认无独立卡；
    中国象棋 kp_card_chess 存量补题——走法典故角度与 QB-1365 不重复）。
预检已过（QB-1735~1737 可用；潮汐/围棋/酸碱中和均已覆盖跳过）。
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
    ("kp_card_intlchess",
     "国际象棋规则",
     "棋类规则知识点内容（人话接口）", "艺术学堂",
     "国际象棋——世界上最流行的棋类：①**棋盘棋子**——8×8 共 64 格黑白"
     "交替，双方各 16 子：王、后、双车、双象、双马、八兵，白方先行；"
     "②**走法**——后直线斜线任意远（最强子）、车直线、象斜线各守一色"
     "格、马走「日」但无蹩马腿、王每格一步；兵只进不退（首步可进两格"
     "），吃子走斜前一格；③**王车易位**——王向车方向横移两格、车跳到"
     "王另一侧（一回合动两子），条件：王与该车都未动过、中间无子、王"
     "不在被将军或经过受攻击的格子，每局每方限一次；④**兵的特权**——"
     "到底线可升变为后/车/象/马（通常升后）；吃过路兵：对方兵首步进两"
     "格越过己兵攻击格时，下一手可斜吃；⑤**胜负**——将死（王被攻击"
     "且无法解脱）获胜；无子可动又未被将则是逼和（和棋）。起源于印度"
     "「恰图兰卡」，经波斯传入欧洲定型。",
     ["国际象棋怎么玩", "王车易位是什么", "兵升变", "吃过路兵",
      "国际象棋规则", "国际象棋和中国象棋区别"],
     ["问中国象棋", "问围棋"],
     "atomic", "",
     "国际象棋=8乘8棋盘64格黑白交替双方16子王后双车双象双马八兵白先行"
     "+后直线斜线最强马走日无蹩腿兵只进不退首步可两格吃斜前+王车易位"
     "王横两格车跳另一侧条件都未动过中间无子王不受攻每方限一次+兵到底"
     "线升变后车象马+吃过路兵+将死胜无子可动未将被为逼和+起源印度恰图"
     "兰卡经波斯欧洲定型。"),
]

QUESTIONS = [
    ("QB-1735", "国际象棋有哪些棋子？王车易位是什么规则？",
     "棋类规则", "技术直答",
     ["国际象棋", "王车易位", "棋子", "将死"], "通识拓展501·新卡"),
    ("QB-1736", "国际象棋的兵有什么特殊规则？什么是兵升变？",
     "棋类规则", "技术直答",
     ["兵升变", "吃过路兵", "国际象棋", "底线"], "通识拓展501·新卡"),
    ("QB-1737", "中国象棋的「马走日象走田」是什么？楚河汉界有什么典故？",
     "棋类规则", "技术直答",
     ["马走日", "象走田", "楚河汉界", "中国象棋"], "通识拓展501·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展501"],
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
    bank["version"] = "v7.66"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
