# -*- coding: utf-8 -*-
"""seed_common_527_cards.py · 通识拓展批次527知识卡+题库（幂等）

527：3 张新卡·器物工艺域（四大名扇 kp_card_mingshan /
    五大名窑 kp_card_yaokou / 三大名锦 kp_card_jinduan——
    id 与语义等价卡名双重确认零覆盖；景泰蓝属珐琅已有专卡）。
预检已过（QB-1813~1815 可用）。
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
    ("kp_card_mingshan",
     "四大名扇",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "四大名扇——扇子里的风雅：①**檀香扇**——江苏苏州，檀香木制成，"
     "扇存香在，「扇动生风，藏之有香」；②**火画扇**——广东新会，以"
     "葵扇为底用烙铁作画，火候拿捏分毫不差；③**竹丝扇**——四川自贡"
     "「龚扇」，竹篾细如发丝薄如蝉翼，灯下透光见图案；④**绫绢扇**——"
     "浙江湖州，绫绢面上工笔重彩，团扇雅致；⑤**折扇知识**——折扇一般"
     "认为宋代由日本、高丽传入，明代中后期大盛，苏杭制扇名家辈出；扇"
     "面书画一体的文人雅趣由此大兴。",
     ["四大名扇", "檀香扇", "火画扇", "竹丝扇", "龚扇",
      "折扇是谁发明的"],
     ["问景泰蓝", "问瓷器"],
     "atomic", "",
     "四大名扇=檀香扇苏州扇动生风藏之有香+火画扇广东新会葵扇烙画火候"
     "分毫+竹丝扇自贡龚扇竹篾如丝灯下透光+绫绢扇湖州工笔团扇+折扇宋代"
     "由日本高丽传入明代大盛苏杭名家扇面书画。"),
    ("kp_card_yaokou",
     "宋代五大名窑",
     "器物工艺知识点内容（人话接口）", "传统文化",
     "宋代五大名窑——中国瓷器的黄金时代：①**汝窑**——五大名窑之首，"
     "天青釉温润如玉，「雨过天青云破处」之色，传世品不足百件；②**官"
     "窑**——宋代宫廷自设（南宋郊坛下官窑），紫口铁足、粉青厚釉；"
     "③**哥窑**——釉面开片「金丝铁线」，大开片套小开片，残缺成美"
     "；④**钧窑**——河南禹州，「入窑一色，出窑万彩」的窑变乳光釉，"
     "「钧瓷无对，窑变无双」；⑤**定窑**——五大名窑中唯一以白瓷著称，"
     "刻花印花精美；⑥**后起之秀**——元明清景德镇集大成，青花彩瓷走"
     "向世界，英语中「中国」一词即源自「瓷器」。",
     ["五大名窑是哪五个", "汝窑", "哥窑金丝铁线", "钧窑窑变",
      "定窑白瓷", "雨过天青云破处"],
     ["问景泰蓝", "问青花瓷"],
     "atomic", "",
     "五大名窑=汝官哥钧定+汝窑之首天青温润传世不足百件+官窑紫口铁足粉"
     "青厚釉+哥窑金丝铁线开片残缺成美+钧窑入窑一色出窑万彩窑变无双+定"
     "窑唯一白瓷刻花+景德镇元明清集大成英语中国一词源自瓷器。"),
    ("kp_card_jinduan",
     "三大名锦",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "三大名锦——织出来的锦绣文章：①**云锦**——南京，「寸锦寸金」："
     "大花楼木机需两人配合，一天仅织数厘米，妆金敷彩如天上云霞，2009"
     " 年列入人类非物质文化遗产；②**蜀锦**——成都，历史最悠久的织锦"
     "（汉代已盛，「锦城」「锦江」因它得名）；③**宋锦**——苏州，宋"
     "代发展起来，质地坚柔、配色典雅，用于书画装裱；④**壮锦**——广西"
     "壮族织锦，与三大名锦合称「四大名锦」，浓艳几何纹样；⑤**共同点**"
     "——提花织造、经纬成章，把诗词吉祥图案织进衣裳。",
     ["三大名锦", "云锦", "蜀锦", "宋锦", "壮锦",
      "寸锦寸金"],
     ["问四大名绣", "问景泰蓝"],
     "atomic", "",
     "三大名锦=云锦南京寸锦寸金大花楼木机两人一天数厘米2009人类非遗+"
     "蜀锦成都历史最久锦城锦江因它得名+宋锦苏州书画装裱典雅+壮锦广西"
     "几何浓艳合称四大名锦+提花织造经纬成章。"),
]

QUESTIONS = [
    ("QB-1813", "四大名扇是哪四把扇？各出自哪里？",
     "传统文化", "技术直答",
     ["四大名扇", "檀香扇", "竹丝扇", "火画扇"], "通识拓展527·新卡"),
    ("QB-1814", "宋代五大名窑是哪五个？汝窑为什么被列为之首？",
     "传统文化", "技术直答",
     ["五大名窑", "汝窑", "官哥钧定", "天青釉"], "通识拓展527·新卡"),
    ("QB-1815", "南京云锦为什么说「寸锦寸金」？三大名锦是哪三个？",
     "传统文化", "技术直答",
     ["云锦", "三大名锦", "蜀锦", "宋锦"], "通识拓展527·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展527"],
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
    bank["version"] = "v7.92"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
