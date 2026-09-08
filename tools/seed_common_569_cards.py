# -*- coding: utf-8 -*-
"""seed_common_569_cards.py · 通识拓展批次569知识卡+题库（幂等）

569：1 张新卡·烟具烟俗域（烟具与烟俗 kp_card_yanju——
    id 与语义等价卡名双重确认双零；鼻烟壶 kp_card_binyanhu
    已有专卡查重跳过）。
预检已过（QB-1939~1941 可用）。
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
    ("kp_card_yanju",
     "烟具与烟俗",
     "民俗器物知识点内容（人话接口）", "传统文化",
     "烟具与烟俗——老烟民的家什（史料视角，吸烟有害健康）：①**烟草东"
     "来**——明万历年间烟草自菲律宾吕宋传入中国，音称「淡巴菰」，清初"
     "已遍地种植；②**旱烟袋**——长杆铜锅玉石嘴，配烟荷包；清代纪昀（"
     "纪晓岚）嗜烟如命，巨杆称「纪大烟袋」；③**水烟袋**——乾隆年间盛"
     "行，烟经水过滤咕噜作响，白铜银制是富家陈设；④**烟斗**——西方传"
     "入，木质斗钵；⑤**鼻烟**——已有鼻烟壶专卡；⑥**收藏**——老烟具"
     "的材质（白铜、玛瑙、翡翠、老竹）与工艺是收藏看点。",
     ["烟具", "旱烟袋", "水烟袋", "纪大烟袋",
      "淡巴菰", "烟斗"],
     ["问鼻烟壶", "问文玩核桃"],
     "atomic", "",
     "烟具烟俗=烟草明万历自吕宋传入音称淡巴菰清初遍种+旱烟袋长杆铜锅玉"
     "嘴烟荷包纪晓岚纪大烟袋+水烟袋乾隆盛行水过滤白铜银制富家陈设+烟斗"
     "西方传入木质斗钵+鼻烟壶见专卡+老烟具白铜玛瑙翡翠老竹材质收藏看点"
     "。"),
]

QUESTIONS = [
    ("QB-1939", "旱烟袋和水烟袋有什么区别？水烟袋为什么有水？",
     "传统文化", "技术直答",
     ["旱烟袋", "水烟袋", "烟锅", "过滤"], "通识拓展569·新卡"),
    ("QB-1940", "「纪大烟袋」说的是谁？他有什么嗜好？",
     "历史常识", "技术直答",
     ["纪晓岚", "纪大烟袋", "纪昀", "嗜烟"], "通识拓展569·新卡"),
    ("QB-1941", "烟草是什么时候传入中国的？当时叫什么名字？",
     "历史常识", "技术直答",
     ["烟草", "万历", "吕宋", "淡巴菰"], "通识拓展569·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展569"],
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
    bank["version"] = "v8.34"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
