# -*- coding: utf-8 -*-
"""seed_common_324_cards.py · 通识拓展批次324知识卡+题库（幂等）

324：文化-大同理想（礼运）/文化-老子与道家（诸子百家新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1211/1212+双id可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_datong2",
     "大同理想（《礼运》）",
     "文化知识点内容（人话接口）", "文化",
     "「大同」——儒家描绘的理想社会：①**出处**——《礼记·礼运》孔子对"
     "言偃（子游）讲远古大道之行：②**核心内容**——「大道之行也，天下为"
     "公」——权力公有；「选贤与能，讲信修睦」——选贤任能诚信和睦；"
     "「不独亲其亲，不独子其子」——超越私爱老有所终幼有所长；「货恶其"
     "弃于地也……不必藏于己」——财物共享各尽其力；③**小康对照**——"
     "「大道既隐」后的小康是「天下为家」各亲其亲、礼治维系——大同=理想"
     "目标、小康=现实可及；④**两千年回响**——洪秀全太平天国、康有为"
     "《大同书》、孙中山「天下为公」都援引此理想；⑤**现代对照**——与"
     "共产主义理想、人类命运共同体理念的精神共鸣常被论及（但思想内核与"
     "历史语境不同）。",
     ["大同社会是什么", "天下为公出自哪里", "礼运大同篇",
      "大同和小康的区别", "选贤与能", "大道之行也"],
     ["问桃花源记对比", "问乌托邦思想史"],
     "atomic", "",
     "大同=礼记礼运孔子理想社会+天下为公选贤与能讲信修睦+不独亲其亲"
     "老有所终幼有所长+财物共享各尽其力+小康对照(天下为家礼治维系)+"
     "康有为大同书孙中山天下为公两千年回响。"),
    ("kp_card_laozi2",
     "老子与道家",
     "文化知识点内容（人话接口）", "文化",
     "老子与道家思想：①**其人其书**——老子（李耳）著《道德经》（五千言"
     "八十一章），道家创始人；②**核心概念「道」**——道法自然：宇宙万物"
     "的本源与运行规律，「道可道非常道」——言说不尽的整体；③**辩证法"
     "萌芽**——「祸兮福之所倚，福兮祸之所伏」——对立面相互转化；④"
     "**无为而治**——不是不作为，是不妄为（顺应规律不瞎折腾）——「治"
     "大国若烹小鲜」；⑤**柔弱胜刚强**——「上善若水」「天下莫柔弱于水"
     "，而攻坚强者莫之能胜」——以柔克刚的生存智慧；⑥**影响**——与"
     "儒家互补（进则儒家退则道家），深刻影响中医养生/艺术审美（留白）/"
     "政治哲学，道家思想也是本土宗教道教的哲学源头（二者有区别：道家"
     "是哲学流派，道教是宗教）。",
     ["老子是谁", "道德经讲什么", "道可道非常道什么意思",
      "无为而治", "上善若水", "道家和道教的区别"],
     ["问庄子逍遥游", "问黄老之学"],
     "atomic", "",
     "老子=道家创始人道德经五千言+道法自然宇宙本源规律+祸福相倚辩证"
     "+无为而治非不作为是不妄为烹小鲜+上善若水柔弱胜刚强+与儒家互补"
     "影响中医艺术政治+道家哲学vs道教宗教有别。"),
]

QUESTIONS = [
    ("QB-1211", "「天下为公」的大同理想出自哪里？描绘了怎样的社会？", "文化", "技术直答",
     ["礼运", "大同", "天下为公", "选贤"], "通识拓展324"),
    ("QB-1212", "老子的核心思想是什么？「无为而治」是什么意思？", "文化", "技术直答",
     ["道德经", "道法自然", "无为", "柔弱"], "通识拓展324"),
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
                               "level:L2", "status:verified", "batch:通识拓展324"],
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
    bank["version"] = "v5.94"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
