# -*- coding: utf-8 -*-
"""seed_common_540_cards.py · 通识拓展批次540知识卡+题库（幂等）

540：2 张新卡·手串行话域（手串佛珠 kp_card_shouchuan /
    古玩行话 kp_card_guwanhua——id 与语义等价卡名双重确认双零）。
预检已过（QB-1852~1854 可用）。
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
    ("kp_card_shouchuan",
     "手串佛珠",
     "民俗雅玩知识点内容（人话接口）", "传统文化",
     "手串佛珠——腕上的一串静心：①**佛珠**——本是佛教念珠，用以诵经"
     "计数；标准 108 颗表对治「百八烦恼」，另有 54、27、18 颗等；②**手"
     "串**——念珠世俗化的腕上文玩；菩提三杰：星月菩提、金刚菩提、凤眼"
     "菩提；③**名贵材质**——小叶紫檀（印度产，金星料最珍）、沉香（树"
     "脂结香，沉水为佳）、蜜蜡（琥珀一族）、南红玛瑙（保山凉山料）、青"
     "金石（阿富汗古已有之）；④**盘玩**——木串忌汗忌水：净手盘与棉布"
     "盘交替、多盘多刷常静置氧化；玉石类则「人养玉、玉养人」靠贴身佩戴"
     "；⑤**寓意**——静心、辟邪、结缘，把玩即修行。",
     ["手串", "佛珠", "108颗", "小叶紫檀", "沉香",
      "星月菩提"],
     ["问文玩核桃", "问玉文化"],
     "atomic", "",
     "手串佛珠=佛教念珠诵经计数108颗对治百八烦恼另有54/27/18+手串念珠"
     "世俗化星月金刚凤眼菩提三杰+小叶紫檀印度金星料沉香沉水为佳蜜蜡南"
     "红青金石+木串忌汗忌水净手盘棉布盘交替静置氧化玉类人养玉+静心辟"
     "邪结缘把玩即修行。"),
    ("kp_card_guwanhua",
     "古玩行话",
     "民俗雅玩知识点内容（人话接口）", "传统文化",
     "古玩行话——古玩圈的江湖黑话：①**捡漏**——以低价买到真品好货，"
     "是每个藏家的梦；**打眼**——看走眼买了假货，交学费；②**掌眼**——"
     "请行家帮着鉴定把关；**开门**——真品特征一目了然（「开门见山」"
     "）；**埋地雷**——卖家设局把假货「埋」在买主眼前；③**包浆**——"
     "器物经年摩挲氧化形成的温润光泽，是岁月包的浆；④**鬼市**——凌晨"
     "开市天光即散的旧货早市，灯光下看货不退不换，全凭眼力；⑤**规矩**"
     "——上手轻拿轻放、看货不砍价先、成交不悔——行内信用大过一切。",
     ["古玩行话", "捡漏", "打眼", "掌眼", "包浆",
      "鬼市"],
     ["问文玩核桃", "问鼻烟壶"],
     "atomic", "",
     "古玩行话=捡漏低价得真品打眼看走眼交学费+掌眼请行家鉴定开门真品"
     "特征明显+埋地雷设局卖假+包浆岁月摩挲氧化温润光泽+鬼市凌晨开市天"
     "光即散不退不换+轻拿轻放看货不砍价成交不悔信用大过一切。"),
]

QUESTIONS = [
    ("QB-1852", "佛珠为什么是108颗？手串的菩提有哪些？",
     "传统文化", "技术直答",
     ["佛珠", "108颗", "星月菩提", "金刚菩提"], "通识拓展540·新卡"),
    ("QB-1853", "小叶紫檀和沉香手串怎么盘？有什么讲究？",
     "传统文化", "技术直答",
     ["小叶紫檀", "沉香", "盘玩", "忌汗"], "通识拓展540·新卡"),
    ("QB-1854", "古玩行话里的「捡漏」和「打眼」是什么意思？",
     "传统文化", "技术直答",
     ["捡漏", "打眼", "行话", "掌眼"], "通识拓展540·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展540"],
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
    bank["version"] = "v8.05"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
