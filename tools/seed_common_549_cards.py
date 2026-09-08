# -*- coding: utf-8 -*-
"""seed_common_549_cards.py · 通识拓展批次549知识卡+题库（幂等）

549：2 张新卡·婚俗古建域（传统婚俗 kp_card_hunsu /
    影壁照壁 kp_card_yingbi——id 与语义等价卡名双重确认双零；
    超时重复写入教训：remember 超时≠失败，回补前必须二次 search 确认）。
预检已过（QB-1879~1881 可用）。
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
    ("kp_card_hunsu",
     "传统婚俗",
     "民俗知识点内容（人话接口）", "传统文化",
     "传统婚俗——三书六礼的千年仪式：①**三书**——聘书（订亲之书）、"
     "礼书（过礼清单）、迎书（迎娶之书）；②**六礼**——纳采（提亲）、"
     "问名（互换八字）、纳吉（卜得吉兆通知）、纳征（送聘礼定亲）、请期"
     "（择定婚期）、亲迎（新郎迎娶）——源于周礼，是古代婚姻的法定流程"
     "；③**花轿与拜堂**——新娘乘花轿至夫家，跨火盆去晦气，一拜天地、"
     "二拜高堂、夫妻对拜，入洞房后新郎以秤杆挑起红盖头（「称心如意」"
     "）；④**吉祥物**——红枣花生桂圆莲子寓意「早生贵子」；⑤**如今**"
     "——中式婚礼复兴，汉式明式婚礼仪式多复原六礼。",
     ["传统婚俗", "三书六礼", "六礼", "花轿",
      "拜堂", "红盖头"],
     ["问宴席座次", "问灯笼民俗"],
     "atomic", "",
     "传统婚俗=三书聘书礼书迎书+六礼纳采问名纳吉纳征请期亲迎源于周礼"
     "法定流程+花轿跨火盆一拜天地二拜高堂夫妻对拜秤杆挑红盖头称心如意"
     "+红枣花生桂圆莲子早生贵子+中式婚礼复兴复原六礼。"),
    ("kp_card_yingbi",
     "影壁照壁",
     "传统建筑知识点内容（人话接口）", "传统文化",
     "影壁照壁——大门内的一面屏障：①**是什么**——大门内（或外）正对"
     "大门的独立短墙，又称照壁、萧墙；②**功能**——遮挡视线护隐私（"
     "「庭院深深」）、风水上「藏风聚气」聚财、进门先见影壁免一览无余"
     "，也是身份品位的展示面；③**构造与装饰**——砖雕吉语（「鸿禧」「"
     "迎祥」）、山水花鸟，下有基座上有瓦顶；④**名品**——九龙壁是最高"
     "等级照壁：北京故宫皇极门、北海公园与山西大同各一座，双面九龙盘踞"
     "；⑤**成语**——「祸起萧墙」的萧墙即宅内照壁，喻祸乱生于内部。",
     ["影壁", "照壁", "九龙壁", "萧墙",
      "四合院影壁", "祸起萧墙"],
     ["问四合院", "问传统婚俗"],
     "atomic", "",
     "影壁照壁=大门内正对独立短墙又称萧墙+遮挡视线藏风聚气免一览无余"
     "身份展示+砖雕吉语鸿禧迎祥基座瓦顶+九龙壁最高级故宫皇极门北海大同"
     "三座双面九龙+祸起萧墙喻祸乱生于内部。"),
]

QUESTIONS = [
    ("QB-1879", "传统婚礼的「三书六礼」分别指什么？",
     "传统文化", "技术直答",
     ["三书六礼", "纳采", "亲迎", "婚俗"], "通识拓展549·新卡"),
    ("QB-1880", "「跨火盆」「挑红盖头」是什么婚礼习俗？有什么寓意？",
     "传统文化", "技术直答",
     ["跨火盆", "红盖头", "拜堂", "习俗"], "通识拓展549·新卡"),
    ("QB-1881", "影壁（照壁）有什么作用？最著名的九龙壁在哪里？",
     "传统文化", "技术直答",
     ["影壁", "照壁", "九龙壁", "萧墙"], "通识拓展549·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展549"],
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
    bank["version"] = "v8.14"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
