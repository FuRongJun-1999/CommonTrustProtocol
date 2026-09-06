# -*- coding: utf-8 -*-
"""seed_common_322_cards.py · 通识拓展批次322知识卡+题库（幂等）

322：科技-钢笔吸墨原理/数学-三角函数基础
KCCS 四要素+题干原句触发词。预检已过（QB-1205/1206+双id可用）。
注：QB-326 铅笔芯角度避让。
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
             "BCS", "B2H6", "borrow", "Rust", "Dijkstra", "Bellman",
             "Floyd", "logV", "sin", "cos", "tan"}


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
    ("kp_card_fountainpen",
     "钢笔吸墨原理",
     "生活科技知识点内容（人话接口）", "生活常识",
     "钢笔怎么把墨水「吸」进去：①**核心=大气压差**——捏皮胆/拉活塞排空"
     "笔胆内空气，松开后胆内气压远小于外界大气压，大气压把墨水「压」进"
     "笔胆（不是笔把墨「吸」进来——主动力是大气压）；②**笔尖结构**——"
     "笔尖中缝（引水槽）靠毛细作用把墨水持续引到纸面，铱粒尖端耐磨；"
     "③**为什么甩不出墨**——毛细+大气压双重锁定（除非挤压胆体或笔尖"
     "漏气）；④**常见故障**——断墨=笔尖缝过大或墨水干涸堵塞（温水浸泡"
     "清洗）；漏墨=气压变化（乘飞机压力差，满胆或空胆携带最安全）；⑤"
     "**毛细现象同类**——纸巾吸水、植物导管运水、灯芯吸油都是同一物理"
     "原理。",
     ["钢笔为什么能吸墨水", "钢笔吸墨原理", "大气压",
      "钢笔为什么甩不出墨", "毛细现象", "钢笔断墨怎么办"],
     ["问墨水成分", "问钢笔品牌工艺"],
     "atomic", "",
     "钢笔吸墨=排空笔胆后大气压把墨压入(主动力是大气压非吸)+笔尖中缝"
     "毛细引水到纸面+毛细大气压双锁定甩不出+断墨温水清洗+乘机压力差满"
     "胆或空胆携带+毛细同类纸巾吸水植物导管灯芯。"),
    ("kp_card_trig3",
     "三角函数基础",
     "数学知识点内容（人话接口）", "数学",
     "三角函数入门：①**定义**——直角三角形中：正弦 sin=对边/斜边、余弦"
     "cos=邻边/斜边、正切 tan=对边/邻边（锐角三角比）；②**特殊角数值**"
     "——30°(1/2,√3/2)、45°(√2/2,√2/2)、60°(√3/2,1/2)——需熟记；③"
     "**关系式**——sin²+cos²=1（勾股关系）、tan=sin/cos；④**扩展到"
     "任意角**——单位圆定义（终边与单位圆交点坐标即 cos、sin），周期 "
     "360°（2π）；⑤**应用**——测高测距（仰角俯角）、物理振动与波（"
     "正弦振动）、交流电（正弦交流）、导航定位；⑥**弧度制**——弧长="
     "半径时的角为 1 弧度，180°=π 弧度（高等数学统一用弧度）。",
     ["三角函数是什么", "正弦余弦正切", "特殊角三角函数值",
      "sin平方加cos平方", "弧度制", "三角函数的应用"],
     ["问诱导公式", "问反三角函数"],
     "atomic", "",
     "三角函数=sin对/斜cos邻/斜tan对/邻(直角三角形)+特殊角30/45/60熟记"
     "+sin²+cos²=1勾股关系+单位圆定义扩展任意角周期2π+应用测高测距振动"
     "波交流电+弧度制180°=π。"),
]

QUESTIONS = [
    ("QB-1205", "钢笔为什么能吸墨水？写的时候墨水为什么不会甩出来？", "生活常识", "技术直答",
     ["大气压", "毛细", "笔胆", "引水"], "通识拓展322"),
    ("QB-1206", "正弦、余弦、正切是怎么定义的？特殊角的三角函数值是多少？",
     "数学", "学科直答",
     ["对边", "斜边", "30", "45"], "通识拓展322"),
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
                               "level:L2", "status:verified", "batch:通识拓展322"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.92"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
