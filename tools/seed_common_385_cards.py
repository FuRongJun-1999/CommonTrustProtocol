# -*- coding: utf-8 -*-
"""seed_common_385_cards.py · 通识拓展批次385知识卡+题库（幂等）

385：1 张存量卡补题（球类运动规则 kp_card_ballsports，乒乓球计分）
    + 2 张新卡（太极拳 kp_card_taichi / 相声 kp_card_crosstalk）。
KCCS 四要素+题干原句触发词。预检已过（QB-1393~1395 可用，
太极拳/相声题库卡库双零，乒乓球题库 0 覆盖）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


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
    ("kp_card_taichi",
     "太极拳",
     "传统武术知识点内容（人话接口）", "传统文化",
     "太极拳——中国代表性传统武术与健身运动：①**起源**——主流考证为"
     "明末清初河南温县陈家沟陈王廷所创；「张三丰创拳」属传说附会；后"
     "衍生出陈式（刚柔并济、发劲明显）、杨式（舒展柔和）、吴式、武式、"
     "孙式等流派；②**运动特点**——圆弧连贯、以柔克刚、刚柔相济、呼吸"
     "与动作配合；技击讲「引进落空」「四两拨千斤」——不硬拼力量，借力"
     "化力；③**练习形式**——套路（如二十四式简化太极拳）、推手（双人"
     "粘黏练习听劲）、器械（剑/刀/扇）；④**健身价值**——改善平衡能力"
     "与下肢力量、调节呼吸与神经系统，节奏可缓可疾，老少皆宜；⑤**"
     "地位**——2020 年列入人类非物质文化遗产代表作名录。",
     ["太极拳是谁发明的", "太极拳有哪些流派", "太极拳的好处",
      "二十四式太极拳", "太极拳推手", "四两拨千斤"],
     ["问八段锦", "问咏春拳"],
     "atomic", "",
     "太极拳=明末清初陈家沟陈王廷创张三丰属传说+陈杨吴武孙五大流派+"
     "圆弧连贯以柔克刚引进落空四两拨千斤+套路推手器械三种练法+改善平"
     "衡下肢力量调节呼吸老少皆宜+2020年人类非遗。"),
    ("kp_card_crosstalk",
     "相声",
     "曲艺常识知识点内容（人话接口）", "传统文化",
     "相声——中国代表性曲艺形式：①**起源**——清代咸丰、同治年间成形"
     "于北京天桥一带，朱绍文（艺名「穷不怕」）是公认的重要奠基人；"
     "天津也是相声重镇（「北京学艺，天津扬名」）；②**四门基本功**——"
     "说（说贯口/绕口令/讲故事）、学（学方言/戏曲/叫卖声）、逗（抖"
     "包袱制造笑料）、唱（太平歌词）；③**表演形式**——单口相声（一人"
     "）、对口相声（逗哏+捧哏两人，最常见）、群口相声（三人以上）；"
     "④**核心手法**——「包袱」：铺垫（系包袱）+抖开（翻包袱）的笑料"
     "组织结构；捧哏的「蹬谝踹卖」配合节奏；⑤**地位**——2008 年列入"
     "国家级非物质文化遗产名录。",
     ["相声的四门功课是什么", "说学逗唱", "相声是谁发明的",
      "单口对口群口相声", "包袱是什么意思", "捧哏逗哏"],
     ["问评书", "问快板"],
     "atomic", "",
     "相声=清咸丰同治年间北京天桥成形朱绍文穷不怕奠基天津扬名+说学逗"
     "唱四门基本功+单口对口（逗哏捧哏）群口三种形式+包袱=铺垫系抖开"
     "翻的笑料结构+2008年国家级非遗。"),
]

QUESTIONS = [
    ("QB-1393", "乒乓球比赛怎么计分？11分制的规则是什么？",
     "体育常识", "技术直答",
     ["乒乓球", "计分", "换发", "规则"], "通识拓展385·存量卡补题"),
    ("QB-1394", "太极拳是谁创立的？练太极拳有什么好处？",
     "传统文化", "技术直答",
     ["太极拳", "陈家沟", "流派", "健身"], "通识拓展385"),
    ("QB-1395", "相声的说学逗唱是什么？单口和对口相声有什么区别？",
     "传统文化", "技术直答",
     ["相声", "说学逗唱", "对口", "包袱"], "通识拓展385"),
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
                               "level:L2", "status:verified", "batch:通识拓展385"],
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
    bank["version"] = "v6.55"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
