# -*- coding: utf-8 -*-
"""seed_common_512_cards.py · 通识拓展批次512知识卡+题库（幂等）

512：1 张新卡 + 1 张存量卡补题·古都民俗域
    （中国古都 kp_card_gudu 新卡——按卡名精确确认双零；
    猜灯谜起源补题挂庙会卡 kp_card_templefair——卡内已有宋代始线索；
    茶马古道 kp_card_teahorse2 已有卡查重跳过）。
预检已过（QB-1768~1770 可用）。
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
    ("kp_card_gudu",
     "中国古都",
     "历史地理知识点内容（人话接口）", "历史与文明",
     "中国古都——王朝定都的选择密码：①**四大古都**——西安（西周丰镐"
     "、秦咸阳、汉长安、隋唐长安，号称十三朝古都）、洛阳（东周、东汉"
     "、曹魏、西晋等，九朝或十三朝之说，「洛阳纸贵」）、南京（东吴、"
     "东晋与南朝宋齐梁陈，故称「六朝古都」，明初亦都于此）、北京（元"
     "大都、明、清三朝）；②**八大古都**——在四大之上加开封（北宋汴"
     "京，《清明上河图》所绘）、杭州（南宋临安）、安阳（商殷墟所在）"
     "、郑州（商代早期都城）；③**定都逻辑**——西安洛阳据关中河洛形"
     "胜控天下、南京凭长江天堑富庶江南、北京扼燕山连东北草原，经济中"
     "心东移南迁推动都城东迁南移；④**文物名片**——西安兵马俑、洛阳"
     "白马寺龙门、南京明孝陵、北京故宫长城。",
     ["中国四大古都", "十三朝古都是哪", "六朝古都是哪",
      "八大古都", "开封为什么是古都", "历代都城"],
     ["问丝绸之路", "问大运河"],
     "atomic", "",
     "中国古都=四大古都西安洛阳南京北京+西安十三朝丰镐咸阳长安+南京"
     "六朝东吴东晋宋齐梁梁陈+北京元明清+八大加开封汴京清明上河图杭州"
     "临安安阳殷墟郑州商城+定都逻辑关中河洛形胜长江天堑燕山要冲经济东"
     "移南迁。"),
]

QUESTIONS = [
    ("QB-1768", "中国四大古都是哪四座城市？西安为什么被称为十三朝古都？",
     "历史常识", "技术直答",
     ["四大古都", "西安", "长安", "十三朝"], "通识拓展512·新卡"),
    ("QB-1769", "「六朝古都」指的是哪座城市？六朝分别指哪些朝代？",
     "历史常识", "技术直答",
     ["六朝古都", "南京", "东吴", "东晋"], "通识拓展512·新卡"),
    ("QB-1770", "猜灯谜的习俗起源于哪个朝代？通常在什么节日？",
     "传统文化", "技术直答",
     ["猜灯谜", "宋代", "元宵节", "赏灯"], "通识拓展512·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展512"],
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
    bank["version"] = "v7.77"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
