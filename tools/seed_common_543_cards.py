# -*- coding: utf-8 -*-
"""seed_common_543_cards.py · 通识拓展批次543知识卡+题库（幂等）

543：2 张新卡·旧物舆图域（舆图收藏 kp_card_ditu /
    老物件收藏 kp_card_yututu——id 与语义等价卡名双重确认双零）。
预检已过（QB-1861~1863 可用）。
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
    ("kp_card_ditu",
     "舆图收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "舆图收藏——收藏一片旧山河：①**舆图**——古称地图为「舆图」（舆"
     "即大地），西晋裴秀立「制图六体」，是中国传统制图学的理论基石；"
     "②**康熙皇舆全览图**——康熙命传教士与中国学者用三角测量法实地测"
     "绘，1718 年成图，是当时世界上领先的全国实测地图；③**航海舆图**"
     "——《郑和航海图》收录于《武备志》，是现存最早的远洋航海图之一；"
     "④**收藏看点**——看年代（纪年与刻工）、看疆域画法（反映当时的世"
     "界知识）、看装裱品相；⑤**意义**——一图一山河，舆图既是疆域史证"
     "据，也是古人世界观的可视化。",
     ["舆图", "康熙皇舆全览图", "郑和航海图", "制图六体",
      "古地图", "舆图收藏"],
     ["问善本收藏", "问郑和下西洋"],
     "atomic", "",
     "舆图收藏=舆即大地古称地图西晋裴秀制图六体理论基石+康熙皇舆全览"
     "图1718传教士三角测量实测世界领先+郑和航海图武备志收录远洋航海图"
     "先驱+看年代疆域画法品相+一图一山河疆域史据世界观可视化。"),
    ("kp_card_yututu",
     "老物件收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "老物件收藏——收藏时代的切片：①**票证**——粮票、布票、油票、工"
     "业券：1955 年起计划经济的票证记忆，1993 年前后退出历史舞台，「全"
     "国通用粮票」最常见也最有时代感；②**通讯旧物**——BP 机、「大哥大"
     "」手提电话，一部通讯进化史；③**生活旧物**——搪瓷缸、煤油灯、缝"
     "纫机、二八大杠自行车；④**收藏态度**——不求贵，求「有故事」：一"
     "件旧物是一代人的共同记忆；⑤**建议**——关注成套性（同一套票证集"
     "齐更珍贵）与品相，防潮防晒妥善存放。",
     ["老物件收藏", "粮票", "票证时代", "BP机",
      "搪瓷缸", "旧物"],
     ["问古玩行话", "问集邮"],
     "atomic", "",
     "老物件收藏=粮票布票油票工业券1955票证记忆1993退出全国通用粮票最"
     "常见+BP机大哥大通讯进化史+搪瓷缸煤油灯缝纫机二八大杠+不求贵求有"
     "故事一代人共同记忆+成套性品相防潮防晒。"),
]

QUESTIONS = [
    ("QB-1861", "古代把地图叫什么？《康熙皇舆全览图》有什么地位？",
     "历史常识", "技术直答",
     ["舆图", "康熙皇舆全览图", "1718", "实测"], "通识拓展543·新卡"),
    ("QB-1862", "西晋裴秀的「制图六体」是什么？",
     "历史常识", "技术直答",
     ["裴秀", "制图六体", "计里画方", "制图学"], "通识拓展543·新卡"),
    ("QB-1863", "粮票是什么时候使用的？为什么有票证时代？",
     "历史常识", "技术直答",
     ["粮票", "票证时代", "1955", "计划经济"], "通识拓展543·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展543"],
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
    bank["version"] = "v8.08"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
