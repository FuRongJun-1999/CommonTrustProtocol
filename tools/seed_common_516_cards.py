# -*- coding: utf-8 -*-
"""seed_common_516_cards.py · 通识拓展批次516知识卡+题库（幂等）

516：2 张新卡·谴责小说收尾（官场现形记 kp_card_guanchang /
    孽海花 kp_card_niehaihua——id 与语义等价卡名双重确认零覆盖，
    与老残游记卡合补晚清四大谴责小说）。
预检已过（QB-1780~1782 可用）。
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
    ("kp_card_guanchang",
     "官场现形记",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《官场现形记》——晚清谴责小说的开山之作：①**作者**——李宝嘉（"
     "李伯元，1867-1906），江苏武进人，办小报出身，以游戏之笔写愤世"
     "之言；②**体量**——共六十回，1903 年起在上海报上连载，未竟而逝"
     "后由友人续成；③**内容**——一部晚清官场群丑图：卖官鬻爵、钻营"
     "贿赂、欺下媚上，从州县佐杂到督抚将军无一幸免；名场面「制台见洋"
     "人」把对内作威作福、对奴颜媚骨的的双面嘴脸写透；④**笔法**——"
     "夸张漫画化，人人皆可笑、事事皆荒唐，鲁迅评这类小说「辞气浮露，"
     "笔无藏锋」——痛快却欠含蓄；⑤**意义**——开创「谴责小说」潮流"
     "，《二十年目睹之怪现状》等皆步其后尘。",
     ["官场现形记是谁写的", "李伯元", "李宝嘉", "谴责小说开山",
      "制台见洋人", "官场现形记讲什么"],
     ["问儒林外史", "问孽海花"],
     "atomic", "",
     "官场现形记=李宝嘉李伯元江苏武进六十回1903年上海连载友人续成+晚"
     "清官场群丑图卖官鬻爵钻营贿赂+制台见洋人对内作威对外媚骨双面嘴"
     "脸+夸张漫画化鲁迅评辞气浮露笔无藏锋痛快欠含蓄+开创谴责小说潮流"
     "。"),
    ("kp_card_niehaihua",
     "孽海花",
     "古典文学知识点内容（人话接口）", "艺术学堂",
     "《孽海花》——清末社会的历史画卷：①**作者**——初由金松岑起笔，"
     "曾朴（1872-1935，江苏常熟人）续成并多次增订，通行三十五回；②**"
     "主线**——状元金雯青与名妓傅彩云的婚姻浮沉（原型即状元外交官洪"
     "钧与赛金花），借一段孽缘串起清末三十年的政治、外交与社会风情；"
     "③**结构**——鲁迅评「结构工巧，文采斐然」：如珠花式串联，人物"
     "事件由主线辐射铺展，与《官场现形记》的平面罗列不同；④**内容**——"
     "科场士风、使节出洋、维新思潮、官僚洋相俱入笔端，是晚清知识界的"
     "一面镜子；⑤**地位**——晚清四大谴责小说之一，与《老残游记》同"
     "属其中艺术性较高者。",
     ["孽海花是谁写的", "曾朴", "金雯青", "傅彩云", "赛金花",
      "孽海花讲什么"],
     ["问老残游记", "问官场现形记"],
     "atomic", "",
     "孽海花=金松岑起笔曾朴常熟人续成增订通行三十五回+状元金雯青名妓"
     "傅彩云影射洪钧赛金花孽缘串清末三十年政治外交社会+鲁迅评结构工巧"
     "文采斐然珠花式串联+科场士风使节出洋维新思潮+四大谴责小说艺术性"
     "较高。"),
]

QUESTIONS = [
    ("QB-1780", "《官场现形记》的作者是谁？这部书批判了什么？",
     "文学常识", "技术直答",
     ["官场现形记", "李伯元", "李宝嘉", "官场腐败"], "通识拓展516·新卡"),
    ("QB-1781", "《孽海花》的男女主角是谁？曾朴在书中扮演什么角色？",
     "文学常识", "技术直答",
     ["孽海花", "曾朴", "金雯青", "傅彩云"], "通识拓展516·新卡"),
    ("QB-1782", "鲁迅如何评价《孽海花》的结构？它与《官场现形记》有何不同？",
     "文学常识", "技术直答",
     ["孽海花", "结构工巧", "鲁迅", "珠花式"], "通识拓展516·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展516"],
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
    bank["version"] = "v7.81"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
