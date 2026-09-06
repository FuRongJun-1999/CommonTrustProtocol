# -*- coding: utf-8 -*-
"""seed_common_306_cards.py · 通识拓展批次306知识卡+题库（幂等）

306：历史-灵渠（沟通两大水系）/工程-都江堰的工程原理
KCCS 四要素+题干原句触发词。预检已过（QB-1150/1151+双id可用）。
注：QB-660 都江堰建者与天府之国已有，本卡取工程科学角度避让。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("kp_card_lingqu",
     "灵渠：沟通两大水系",
     "历史知识点内容（人话接口）", "历史",
     "灵渠——世界上最古老的运河之一：①**背景**——秦始皇统一岭南（前 214"
     " 年前后），军粮运输受南岭阻隔，命史禄开凿运河沟通湘江（长江水系）"
     "与漓江（珠江水系）；②**世界级难点**——两江水位差数米，水量不同，"
     "古人是怎么让船「爬坡」的；③**巧思三件套**——铧嘴（分水堤把湘水"
     "三七分派入湘漓两江）+大小天平（溢流坝稳定水位）+陡门（世界最早的"
     "船闸雏形，36 座逐级蓄水放水让船「逐级爬坡」——比欧洲船闸早千年）；"
     "④**意义**——运河一通岭南入版图，中原与岭南经济文化贯通两千年"
     "（灵渠至今仍在灌溉）；⑤**与长城的对照**——同为秦代超级工程：长城"
     "是「拒」的防御，灵渠是「通」的连接——一堵一疏塑造了两种治理逻辑。",
     ["灵渠是谁开凿的", "灵渠沟通了哪两大水系", "陡门是什么",
      "灵渠为什么能通航", "秦始皇统一岭南", "铧嘴分水"],
     ["问京杭大运河对比", "问岭南开发史"],
     "atomic", "",
     "灵渠=前214年史禄奉秦始皇命沟通湘江(长江)漓江(珠江)+铧嘴分水三七"
     "分派+大小天平溢流稳水位+36陡门=世界最早船闸雏形让船逐级爬坡"
     "(早欧洲千年)+岭南入版图两千年贯通+与长城一堵一疏两种治理逻辑。"),
    ("kp_card_djyeng",
     "都江堰的工程原理",
     "工程通识知识点内容（人话接口）", "历史",
     "都江堰为什么两千年不衰：①**无坝引水**——不拦江筑坝，顺应水势把"
     "岷江水「引」向成都平原（李冰父子前 256 年主持）；②**鱼嘴分水堤**——"
     "把岷江分成内江（灌溉）外江（排洪）：枯水季六成入内江保灌溉，洪水季"
     "六成走外江保安全——自动按水量分配（弯道环流原理：表层清水向内江"
     "底层泥沙向外江）；③**飞沙堰**——内江水位过高时自动漫顶泄洪+利用"
     "弯道把泥沙甩入外江（排沙）；④**宝瓶口**——玉垒山人工凿开的引水"
     "咽喉（火烧水激开山法），控制进水总量；⑤**系统哲学**——鱼嘴分水+"
     "飞沙堰排沙泄洪+宝瓶口控流，三组件互相配合「乘势利导、因时制宜」"
     "——不与水对抗而是顺应；⑥**深淘滩低作堰**——六字治水方针沿用至今，"
     "每年岁修制度让工程自我维护两千年。",
     ["都江堰的原理", "鱼嘴分水堤", "飞沙堰的作用", "宝瓶口",
      "深淘滩低作堰", "弯道环流"],
     ["问郑国渠", "问古代水利对比"],
     "atomic", "",
     "都江堰=前256李冰无坝引水+鱼嘴分水(枯六入内保灌洪六走外自动分配·"
     "弯道环流清水向内沙向外)+飞沙堰漫顶泄洪甩沙+宝瓶口控流咽喉+三组件"
     "乘势利导不与水对抗+深淘滩低作堰六字方针岁修两千年。"),
]

QUESTIONS = [
    ("QB-1150", "灵渠沟通了哪两大水系？陡门有什么作用？", "历史", "技术直答",
     ["湘江", "漓江", "陡门", "船闸"], "通识拓展306"),
    ("QB-1151", "都江堰的鱼嘴和飞沙堰分别起什么作用？为什么两千年不衰？",
     "历史", "技术直答",
     ["鱼嘴", "分水", "飞沙堰", "泄洪"], "通识拓展306"),
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
                               "level:L2", "status:verified", "batch:通识拓展306"],
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
    bank["version"] = "v5.76"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
