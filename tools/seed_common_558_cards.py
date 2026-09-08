# -*- coding: utf-8 -*-
"""seed_common_558_cards.py · 通识拓展批次558知识卡+题库（幂等）

558：1 张新卡·神魔小说域（封神演义与姜子牙 kp_card_fengshen——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1906~1908 可用）。
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
    ("kp_card_fengshen",
     "封神演义与姜子牙",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《封神演义》与姜子牙——封神榜上的神魔大战：①**小说**——明代百"
     "回神魔小说（通行题许仲琳著），以武王伐纣、商周交替为背景，纣王宠"
     "妲己失德，姜子牙辅佐周室，截教阐教斗法，终封三百六十五路正神；"
     "②**姜子牙**——姜尚字子牙，渭水磻溪直钩钓鱼「宁在直中取，不向曲"
     "中求」，愿者上钩；传说文王拉车八百步、周室八百年；辅周灭商后封于"
     "齐，被尊为兵家鼻祖、「百家宗师」；③**哪吒闹海**——陈塘关李靖三"
     "子哪吒闹海打死龙王三太子，剔骨还父割肉还母，太乙真人以莲花莲藕为"
     "其重塑肉身，脚踏风火轮手持火尖枪；④**名场面**——比干剖心、姜王"
     "后遭陷、梅山七怪、万仙阵；⑤**影响**——封神榜体系滋养了后世戏曲"
     "、评书、影视与游戏的世界观。",
     ["封神演义", "姜子牙", "哪吒闹海", "姜太公钓鱼",
      "封神榜", "武王伐纣"],
     ["问西游记", "问妲己"],
     "atomic", "",
     "封神演义=明代百回神魔小说通行题许仲琳武王伐纣商周交替纣王妲己+"
     "姜子牙渭水直钩钓鱼愿者上钩文王拉车八百步周八百年封于齐兵家鼻祖+"
     "截教阐教斗法封三百六十五路正神+哪吒闹海剔骨还父莲花化身风火轮+"
     "比干剖心万仙阵名场面滋养戏曲评书影视游戏。"),
]

QUESTIONS = [
    ("QB-1906", "《封神演义》讲的是什么朝代的故事？作者是谁？",
     "文学常识", "技术直答",
     ["封神演义", "武王伐纣", "许仲琳", "神魔"], "通识拓展558·新卡"),
    ("QB-1907", "「姜太公钓鱼，愿者上钩」的典故是什么？",
     "文学常识", "技术直答",
     ["姜太公", "姜子牙", "渭水", "文王"], "通识拓展558·新卡"),
    ("QB-1908", "哪吒闹海讲的是什么故事？莲花化身是怎么回事？",
     "文学常识", "技术直答",
     ["哪吒闹海", "莲花化身", "龙王", "太乙真人"], "通识拓展558·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展558"],
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
    bank["version"] = "v8.23"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
