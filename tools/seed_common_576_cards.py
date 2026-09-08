# -*- coding: utf-8 -*-
"""seed_common_576_cards.py · 通识拓展批次576知识卡+题库（幂等）

576：2 张新卡·绝技微雕域（川剧变脸 kp_card_bianlian /
    核雕 kp_card_hediao——id 与语义等价卡名双重确认双零）。
预检已过（QB-1960~1962 可用）。
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
    ("kp_card_bianlian",
     "川剧变脸",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "川剧变脸——一转身一张脸的绝技：①**川剧**——流行四川重庆云贵的"
     "地方戏，含昆、高、胡、弹、灯五种声腔，高腔「帮打唱」最有特色；"
     "②**变脸三法**——「抹脸」（手抹额间油彩变脸）、「吹脸」（粉末"
     "吹敷）、「扯脸」（脸谱画在绸子上层层扯下）；变脸速度与保密是行"
     "业绝技，传统上「传内不传外」；③**其他绝活**——吐火、滚灯（顶灯"
     "钻板凳）；④**经典剧目**——《白蛇传》紫金铙钹变脸、《变脸》"
     "（魏明伦编剧）；⑤**地位**——川剧列入国家级非遗，变脸是川剧最"
     "具辨识度的名片。",
     ["川剧", "变脸", "抹脸", "扯脸", "吐火",
      "滚灯"],
     ["问京剧", "问杂技与幻术"],
     "atomic", "",
     "川剧变脸=川渝地方戏昆高胡弹灯五声腔高腔帮打唱+变脸三法抹脸吹脸"
     "扯脸绸子层层扯下传内不传外+吐火滚灯顶灯钻板凳绝活+白蛇传紫金铙"
     "钹变脸魏明伦变脸+国家级非遗川剧名片。"),
    ("kp_card_hediao",
     "核雕",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "核雕——橄榄核上的大千世界：①**课文**——明代魏学洢《核舟记》"
     "：王叔远以「径寸之木」雕苏东坡泛舟赤壁，窗八、人五、箬篷楫炉壶"
     "手卷念珠对联，「计其长曾不盈寸」；②**产地**——苏州光福镇核雕最"
     "负盛名，山东潍坊核雕亦自成一路；③**题材**——罗汉头手串最经典，"
     "另有花鸟、山水、民俗人物；④**玩法**——橄榄核雕上手盘玩，包浆后"
     "色如枣红；⑤**意趣**——「方寸之间现大千」，以最小载体呈现最大"
     "叙事，是微雕审美的代表。",
     ["核雕", "核舟记", "王叔远", "橄榄核",
      "光福核雕", "罗汉头"],
     ["问文玩核桃", "问玉器雕工"],
     "atomic", "",
     "核雕=核舟记明魏学洢王叔远径寸之木苏东坡泛舟赤壁窗八人五曾不盈寸+"
     "苏州光福核雕潍坊核雕两路+罗汉头手串最经典花鸟山水民俗+盘玩包浆枣"
     "红+方寸之间现大千微雕审美代表。"),
]

QUESTIONS = [
    ("QB-1960", "川剧「变脸」有哪些手法？为什么说它是绝技？",
     "传统文化", "技术直答",
     ["川剧", "变脸", "扯脸", "绝技"], "通识拓展576·新卡"),
    ("QB-1961", "《核舟记》里王叔远雕了什么？核舟有多小？",
     "文学常识", "技术直答",
     ["核舟记", "王叔远", "核舟", "魏学洢"], "通识拓展576·新卡"),
    ("QB-1962", "核雕用什么材料？哪个地方的核雕最出名？",
     "传统文化", "技术直答",
     ["核雕", "橄榄核", "光福", "苏州"], "通识拓展576·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展576"],
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
    bank["version"] = "v8.41"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
