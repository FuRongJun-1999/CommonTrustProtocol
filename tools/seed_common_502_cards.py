# -*- coding: utf-8 -*-
"""seed_common_502_cards.py · 通识拓展批次502知识卡+题库（幂等）

502：2 张新卡·神话双域（希腊神话 kp_card_greekmyth /
    北欧神话 kp_card_norsemyth）。
预检已过（QB-1738~1740 可用，两主题按卡名精确确认无独立卡、题库零题）。
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
    ("kp_card_greekmyth",
     "希腊神话",
     "神话文学知识点内容（人话接口）", "艺术学堂",
     "希腊神话——西方文明的神话源头：①**众神之家**——奥林匹斯山十二"
     "主神：天父宙斯（雷电）、天后赫拉（婚姻）、海神波塞冬、冥王哈迪"
     "斯、智慧女神雅典娜（从宙斯头颅中诞生，雅典城的保护神）、太阳神"
     "阿波罗（音乐与预言）、爱与美之神阿佛洛狄忒等；②**盗火者**——"
     "普罗米修斯为人类盗取天火，被宙斯锁在高加索山受罚；③**潘多拉魔"
     "盒**——宙斯报复人类，潘多拉打开魔盒放出一切灾祸，只留下「希望"
     "」；④**特洛伊战争**——金苹果之争引发，帕里斯拐走海伦，希腊联军"
     "十年围城，「特洛伊木马」献城计出自奥德修斯，《荷马史诗·伊利亚"
     "特》记录此战；⑤**文化影响**——奥运会源于奥林匹亚竞技会（献给"
     "宙斯，前 776 年首届有记载），西方文学艺术语汇大量出自希腊神话。",
     ["希腊神话十二主神", "宙斯是谁", "普罗米修斯盗火",
      "潘多拉魔盒是什么", "特洛伊木马计", "奥运会起源"],
     ["问北欧神话", "问荷马史诗"],
     "atomic", "",
     "希腊神话=奥林匹斯十二主神宙斯赫拉波塞冬雅典娜阿波罗+普罗米修斯"
     "盗天火锁高加索山+潘多拉魔盒灾祸只留希望+特洛伊战争金苹果海伦木"
     "马计奥德修斯荷马史诗伊利亚特+奥运源于奥林匹亚竞技会前776年。"),
    ("kp_card_norsemyth",
     "北欧神话",
     "神话文学知识点内容（人话接口）", "艺术学堂",
     "北欧神话——斯堪的纳维亚的神话体系：①**主神**——众神之父奥丁"
     "（独眼，献眼换智慧，骑八足神马斯莱普尼尔）、雷神托尔（奥丁之子"
     "，挥雷神之锤妙尔尼尔掌风暴）、诡计之神洛基（机智善变，酿成大祸"
     "）；②**世界观**——世界树尤克特拉希尔连接九个世界（神国、人间"
     "米德加尔特、巨人国、冥界等）；③**英灵殿瓦尔哈拉**——阵亡勇士"
     "灵魂的归宿，白天厮杀晚上宴饮，等待末日之战；④**诸神黄昏**——"
     "注定到来的末日大战：洛基之子恶狼芬里尔吞掉奥丁，诸神与巨人同归"
     "于尽，世界焚毁后重生——「毁灭与重生」的循环观深刻影响北欧文学"
     "与《魔戒》《雷神》等现代作品；⑤**生活印记**——英语星期名源自北"
     "欧神：星期四是「托尔日」、星期三是「奥丁日」、星期五是「弗丽嘉"
     "日」。",
     ["北欧神话主神是谁", "雷神托尔", "奥丁", "世界树",
      "诸神黄昏是什么", "瓦尔哈拉英灵殿"],
     ["问希腊神话", "问雷神电影"],
     "atomic", "",
     "北欧神话=众神之父奥丁独眼献眼换智慧八足马斯莱普尼尔+雷神托尔之"
     "锤妙尔尼尔洛基诡计之神+世界树尤克特拉希尔连接九界+英灵殿瓦尔哈"
     "拉阵亡勇士归宿+诸神黄昏芬里尔吞奥丁毁灭重生循环影响魔戒雷神+星"
     "期四托尔日星期三奥丁日。"),
]

QUESTIONS = [
    ("QB-1738", "希腊神话的主神宙斯掌管什么？普罗米修斯为什么受罚？",
     "文学常识", "技术直答",
     ["宙斯", "普罗米修斯", "盗火", "奥林匹斯"], "通识拓展502·新卡"),
    ("QB-1739", "特洛伊木马计是谁想出来的？故事结局如何？",
     "文学常识", "技术直答",
     ["特洛伊木马", "奥德修斯", "海伦", "伊利亚特"], "通识拓展502·新卡"),
    ("QB-1740", "北欧神话的奥丁和雷神托尔是什么关系？什么是诸神黄昏？",
     "文学常识", "技术直答",
     ["奥丁", "托尔", "诸神黄昏", "北欧神话"], "通识拓展502·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展502"],
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
    bank["version"] = "v7.67"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
