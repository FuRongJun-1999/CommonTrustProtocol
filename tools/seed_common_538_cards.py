# -*- coding: utf-8 -*-
"""seed_common_538_cards.py · 通识拓展批次538知识卡+题库（幂等）

538：2 张新卡·清供玉雕域（文房清供 kp_card_qinggong /
    玉器雕工 kp_card_yudiao——id 与语义等价卡名双重确认双零）。
预检已过（QB-1846~1848 可用）。
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
    ("kp_card_qinggong",
     "文房清供",
     "传统文化知识点内容（人话接口）", "传统文化",
     "文房清供——文人案头的雅趣天地：①**是什么**——笔墨纸砚之外的文"
     "房陈设雅器总称，又称「文房清玩」；②**诸器分工**——笔筒插笔、笔"
     "洗涮笔、水盂储水（配水注滴研）、镇纸压纸、臂搁搁腕防臂汗污纸、"
     "墨床搁墨锭、笔架笔山挂笔搁笔、印盒盛印泥；③**材质**——瓷、玉、"
     "竹、木、铜、石无所不包，嘉定竹刻、豇豆红水盂皆是名品；④**意趣**"
     "——器物皆小而讲究，一几一案自成天地，是文人审美日常化的体现；"
     "⑤**如今**——文房清供成为收藏热点与国风礼赠首选。",
     ["文房清供", "镇纸", "臂搁", "笔洗", "水盂",
      "笔筒"],
     ["问文房四宝", "问明式家具"],
     "atomic", "",
     "文房清供=笔墨纸砚外文房雅器总称清玩+笔筒插笔笔洗涮笔水盂储水水"
     "注滴研镇纸压纸臂搁护腕防汗墨床搁墨笔架挂笔印盒印泥+瓷玉竹木铜石"
     "嘉定竹刻豇豆红+一几一案自成天地审美日常化+收藏热点国风礼赠。"),
    ("kp_card_yudiao",
     "玉器雕工",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "玉器雕工——刀尖上的巧夺天工：①**俏色巧雕**——依玉料天然色泽因"
     "材施艺：红处雕霞、黑处作发、白处留云，「一料一设计」，全是天工"
     "与人工的合作；②**陆子冈**——明代苏州琢玉圣手，「子冈牌」玉牌一"
     "面山水一面诗文，落款敢与皇帝抢风头；③**薄胎**——受痕都斯坦风格"
     "影响，「在手疑无物，定睛知有形」，乾隆赞不绝口；④**绝活**——掏"
     "膛（整玉挖空薄而匀）、链子活（整料琢出环环相扣的活动链，一链到底"
     "不断）；⑤**精神**——慢工出细活，一件大器动辄数年，「玉不琢不成"
     "器」由此成为育人格言。",
     ["玉器雕工", "俏色", "陆子冈", "子冈牌", "薄胎玉器",
      "链子活"],
     ["问玉文化", "问明式家具"],
     "atomic", "",
     "玉器雕工=俏色巧雕依料施艺红霞黑发白云一料一设计+陆子冈明代苏州"
     "圣手子冈牌山水诗文+薄胎痕都斯坦风格在手疑无物+掏膛整玉挖空链子"
     "活整料活动链环不断+慢工数年玉不琢不成器育人格言。"),
]

QUESTIONS = [
    ("QB-1846", "文房清供指什么？「臂搁」是干什么用的？",
     "传统文化", "技术直答",
     ["文房清供", "臂搁", "镇纸", "笔洗"], "通识拓展538·新卡"),
    ("QB-1847", "玉雕的「俏色」是什么？陆子冈是谁？",
     "传统文化", "技术直答",
     ["俏色", "陆子冈", "子冈牌", "巧雕"], "通识拓展538·新卡"),
    ("QB-1848", "玉器的「链子活」是什么绝活？为什么极难？",
     "传统文化", "技术直答",
     ["链子活", "玉器", "环环相扣", "掏膛"], "通识拓展538·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展538"],
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
    bank["version"] = "v8.03"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
