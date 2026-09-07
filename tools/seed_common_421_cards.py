# -*- coding: utf-8 -*-
"""seed_common_421_cards.py · 通识拓展批次421知识卡+题库（幂等）

421：1 张存量卡补题（世界著名建筑 kp_card_worldbuildings，已在库，
    埃菲尔铁塔与泰姬陵角度）+ 2 张新卡（自由女神像 kp_card_liberty /
    悉尼歌剧院 kp_card_operahouse，题库卡库双零）。
世界地标三连。预检已过（QB-1501~1503 可用，三主题题库 0 覆盖）。
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("kp_card_liberty",
     "自由女神像",
     "世界地标知识点内容（人话接口）", "世界文化",
     "自由女神像——美国纽约的标志：①**来历**——法国人民为纪念美国独立"
     "100 周年、庆祝法美友谊而赠送，1886 年落成于纽约港自由岛；②**"
     "构造**——铜片锤打成型的巨型雕像，高约 46 米（连基座约 93 米），"
     "内由钢铁骨架支撑（工程师埃菲尔——埃菲尔铁塔设计者参与）；右手"
     "火炬、左手铭板（刻《独立宣言》发表日 1776 年 7 月 4 日）、头冠"
     "七道尖芒象征七大洲七大洋；③**寓意**——自由照耀世界，是移民乘"
     "船入美看到的第一座雕像，「美国的门面」；④**冷知识**——铜像"
     "原本是亮铜色，几十年氧化后变成如今的青绿色（铜锈层反而保护了"
     "内部）。",
     ["自由女神像在哪", "自由女神像是谁送的", "自由女神像多高",
      "自由女神像为什么是绿色的", "自由女神右手拿什么", "纽约地标"],
     ["问埃菲尔铁塔", "问美国"],
     "atomic", "",
     "自由女神像=法国赠美国纪念独立百年1886年纽约港自由岛+铜片锤打钢"
     "骨架埃菲尔参与高46米连基座93米+火炬独立宣言铭板七尖芒七洲七洋+"
     "移民入美第一像自由照耀世界+原亮铜色氧化成青绿铜锈保护内部。"),
    ("kp_card_operahouse",
     "悉尼歌剧院",
     "世界地标知识点内容（人话接口）", "世界文化",
     "悉尼歌剧院——20 世纪最具辨识度的建筑之一：①**位置**——澳大利亚"
     "悉尼港贝尼朗岬角，三面环水；②**设计**——丹麦建筑师约恩·乌松"
     "设计，白色「贝壳/风帆」造型屋顶；施工难度极大，原计划 4 年完工"
     "实际用了 14 年（1973 年落成），造价超预算十多倍——成为「理想与"
     "工程妥协」的经典案例；③**地位**——2007 年列入世界文化遗产（"
     "在世建筑师作品入选极为罕见）；是悉尼乃至澳大利亚的文化名片；④**"
     "功能**——不止演歌剧：音乐厅、歌剧厅、戏剧厅多厅一体，年演出"
     "上千场；⑤**趣闻**——屋顶白瓷砖约 100 万块，自清洁设计，雨后"
     "焕然一新。",
     ["悉尼歌剧院在哪", "悉尼歌剧院谁设计的", "悉尼歌剧院像什么",
      "悉尼歌剧院建了多久", "世界文化遗产建筑", "澳大利亚地标"],
     ["问埃菲尔铁塔", "问世界著名建筑"],
     "atomic", "",
     "悉尼歌剧院=澳大利亚悉尼港贝尼朗岬角三面环水+丹麦建筑师乌松设计"
     "白色贝壳风帆屋顶+计划4年实际14年1973落成造价超十多倍理想与工程"
     "妥协经典+2007年世界文化遗产罕见在世建筑师作品+百万白瓷砖自清洁"
     "多厅一体年演出上千场。"),
]

QUESTIONS = [
    ("QB-1501", "埃菲尔铁塔建于哪一年？泰姬陵是为什么而建的？",
     "世界文化", "技术直答",
     ["埃菲尔铁塔", "泰姬陵", "建筑", "地标"], "通识拓展421·存量卡补题"),
    ("QB-1502", "自由女神像是谁送给美国的？它为什么是绿色的？",
     "世界文化", "技术直答",
     ["自由女神像", "法国", "铜绿", "纽约"], "通识拓展421"),
    ("QB-1503", "悉尼歌剧院是谁设计的？它的屋顶像什么？",
     "世界文化", "技术直答",
     ["悉尼歌剧院", "乌松", "设计", "遗产"], "通识拓展421"),
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
                               "level:L2", "status:verified", "batch:通识拓展421"],
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
    bank["version"] = "v6.92"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
