# -*- coding: utf-8 -*-
"""seed_common_534_cards.py · 通识拓展批次534知识卡+题库（幂等）

534：1 张新卡·古代礼仪域（见面礼：作揖跪拜 kp_card_jianmian——
    id 与语义等价卡名双重确认双零；干支生肖 kp_card_stemsbranches
    已有卡查重跳过）。
预检已过（QB-1834~1836 可用）。
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
    ("kp_card_jianmian",
     "古代见面礼",
     "传统文化知识点内容（人话接口）", "传统文化",
     "古代见面礼——一双手里的规矩：①**拱手与作揖**——拱手是双手合抱"
     "举于胸前；作揖再加俯身躬腰。吉拜男子左手包右手（右手惯持凶器，"
     "包住以示无敌意），丧礼反之；女子相反；②**跪拜三等**——「稽首"
     "」头触地久久不起，臣拜君、子拜父的最重礼；「顿首」头触地即起，"
     "平辈之礼（书信开头写「顿首」即由此来）；「空首」头至于手不触地"
     "，君主答臣下之礼；③**万福**——旧时女子礼：双手轻握置于腰侧，"
     "微屈膝道「万福」；④**揖让**——宾主相见互相拱手致意，「揖让而升"
     "」见《论语》；⑤**演变**——握手是近代西方传入的礼节；2020 年以"
     "来拱手礼因无接触重新流行，「见面对揖不握手」渐成新风尚。",
     ["作揖", "拱手", "稽首", "顿首", "万福礼",
      "拱手哪只手包哪只手"],
     ["问宴席座次", "问避讳"],
     "atomic", "",
     "拱手作揖=拱手合抱作揖加俯身+男子吉拜左手包右手右手持凶器示无敌"
     "意丧礼反女子相反+稽首触地久臣拜君最重+顿首触地即起平辈书信顿首"
     "+空首头至手不触地君答臣+万福女子屈膝道万福+握手近代西来拱手无接"
     "触复兴。"),
]

QUESTIONS = [
    ("QB-1834", "「稽首」「顿首」「空首」三种跪拜礼有什么区别？",
     "传统文化", "技术直答",
     ["稽首", "顿首", "空首", "跪拜"], "通识拓展534·新卡"),
    ("QB-1835", "拱手礼应该哪只手包哪只手？做反了会怎样？",
     "传统文化", "技术直答",
     ["拱手", "左手", "右手", "吉拜"], "通识拓展534·新卡"),
    ("QB-1836", "旧时女子行「万福礼」是什么样子？",
     "传统文化", "技术直答",
     ["万福", "女子", "礼节", "屈膝"], "通识拓展534·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展534"],
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
    bank["version"] = "v7.99"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
