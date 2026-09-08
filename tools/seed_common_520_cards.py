# -*- coding: utf-8 -*-
"""seed_common_520_cards.py · 通识拓展批次520知识卡+题库（幂等）

520：2 张新卡·制度商帮域（清代科场案 kp_card_kechang /
    商帮与会馆 kp_card_huiguan——id 与语义等价卡名双重确认双零）。
预检已过（QB-1792~1794 可用）。
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
    ("kp_card_kechang",
     "清代科场案",
     "制度史知识点内容（人话接口）", "历史与文明",
     "清代科场案——科举舞弊的血色代价：①**顺治丁酉科场案**（1657 年）"
     "——顺天、江南两闱乡试同考官受贿卖「关节」（约定暗号录取），案发"
     "后主考同考官多人处死、家产籍没，举人资格吊销并流徙东北，牵连数"
     "百人；②**咸丰戊午科场案**（1858 年）——顺天乡试主考、大学士柏"
     "葰（一品大员）因家人受贿调换试卷，肃顺穷治，柏葰被斩——清代因"
     "科场案处死的最高级别官员，震动朝野；③**防弊手段**——「弥封」"
     "（糊住考生姓名）、「誊录」（朱笔誊抄防认笔迹，宋代已创）、考前"
     "搜检夹带、考官亲属回避、墨卷朱卷比对；④**双刃**——严刑虽吓阻"
     "舞弊，也使考官宁严勿宽；科场案折射科举「公平」二字的千钧之重。",
     ["清代科场案", "丁酉科场案", "柏葰", "戊午科场案",
      "弥封誊录", "科举舞弊怎么防"],
     ["问科举制度", "问汉字六书"],
     "atomic", "",
     "科场案=顺治丁酉1657顺天江南两闱受贿关节主考同考官处死流徙牵连数"
     "百人+咸丰戊午1858主考大学士柏葰家人受贿调卷被斩清代科场案最高级"
     "别肃顺穷治+防弊弥封誊录搜检回避墨卷朱卷+严刑吓阻亦宁严勿宽+公平"
     "二字千钧之重。"),
    ("kp_card_huiguan",
     "商帮与会馆",
     "经济史知识点内容（人话接口）", "历史与文明",
     "商帮与会馆——明清商人的组织智慧：①**十大商帮**——晋商（票号诚"
     "信，详见镖局票号卡）、徽商（「无徽不成镇」「贾而好儒」，代表人物"
     "晚清红顶商人胡雪岩——阜康钱庄巨富后破产）、粤商、闽商、宁波帮、"
     "陕西商帮等并称十大商帮；②**徽商特色**——盐典茶木四业起家，重"
     "教育，「前世不修，生在徽州，十三四岁，往外一丢」的民谣道尽经商"
     "少年离家；③**会馆**——同乡或同业在客居地共建的聚会之所：北京"
     "湖广会馆、苏州全晋会馆、聊城山陕会馆皆有名；④**会馆功能**——联"
     "络乡谊、商议行情、祭祀乡神（如关羽）、办义学义庄、接待同乡食宿"
     "——是同乡信用网络的实体化；⑤**意义**——商帮与会馆构成明清跨"
     "区域贸易的信任基础设施，堪称古代「商会+同乡会+信用社」。",
     ["明清十大商帮", "徽商", "胡雪岩", "会馆是干什么的",
      "湖广会馆", "山陕会馆"],
     ["问镖局与票号", "问漕运与盐政"],
     "atomic", "",
     "商帮会馆=十大商帮晋商徽商粤闽宁波陕西等+徽商无徽不成镇贾而好儒"
     "盐典茶木胡雪岩阜康钱庄破产+会馆同乡同业客居地聚会所湖广全晋山陕"
     "有名+功能联络乡谊议行情祀关羽义学义庄接待+跨区域贸易信任基础设"
     "施商会同乡会信用社。"),
]

QUESTIONS = [
    ("QB-1792", "清代著名的科场案有哪些？朝廷怎么防科举舞弊？",
     "历史常识", "技术直答",
     ["科场案", "丁酉", "柏葰", "弥封誊录"], "通识拓展520·新卡"),
    ("QB-1793", "「无徽不成镇」说的是哪个商帮？它有什么特点？",
     "历史常识", "技术直答",
     ["徽商", "无徽不成镇", "贾而好儒", "胡雪岩"], "通识拓展520·新卡"),
    ("QB-1794", "会馆是干什么的？有哪些著名的会馆？",
     "传统文化", "技术直答",
     ["会馆", "同乡", "湖广会馆", "山陕会馆"], "通识拓展520·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展520"],
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
    bank["version"] = "v7.85"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
