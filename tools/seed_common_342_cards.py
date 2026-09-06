# -*- coding: utf-8 -*-
"""seed_common_342_cards.py · 通识拓展批次342知识卡+题库（幂等）

342：历史-茶马古道/工程-坎儿井（古代通道工程新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1265/1266+双id可用）。
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
    ("kp_card_teahorse2",
     "茶马古道",
     "历史地理知识点内容（人话接口）", "历史",
     "茶马古道——世界最高最险的贸易通道：①**是什么**——唐宋至民国，滇川"
     "与西藏之间以骡马牦牛驮运茶叶/马匹/盐巴/药材的古商道（滇藏线与川藏"
     "线两大主线）；②**为什么用马帮驮茶**——高原雪域急需茶叶（解油腻"
     "补充维生素——游牧民族「宁可三日无粮，不可一日无茶」），内地需要"
     "战马——茶马互市是刚需；③**艰险**——海拔从几百米到五千多米，穿"
     "峡谷越雪山，马帮风餐露宿数月一趟（术语「锅头」领队）；④**文化带**"
     "——沿途城镇（丽江/理塘/康定）因茶马互市兴起，多民族经济文化交融"
     "的走廊；⑤**与丝绸之路对照**——丝路走沙漠绿洲运丝绸西去，茶马道"
     "走高原峡谷运茶叶西进北上，一北一南同为文明动脉；⑥**今日**——"
     "古道多废弃成徒步文化旅游线路，普洱茶因茶马古道扬名。",
     ["茶马古道是什么", "茶马古道在哪里", "为什么用马运茶",
      "茶马互市", "丽江茶马古道", "普洱茶和茶马古道"],
     ["问马帮文化", "问藏区贸易史"],
     "atomic", "",
     "茶马古道=唐宋至民国滇川至西藏骡马驮运茶马盐药古商道+高原需茶解"
     "油腻内地需战马互市刚需+海拔几百至五千余米马帮数月一趟+丽江理塘"
     "康定因道兴起多民族走廊+与丝路一北一南文明动脉+普洱茶因道扬名。"),
    ("kp_card_karez2",
     "坎儿井",
     "工程通识知识点内容（人话接口）", "地理学",
     "坎儿井——地下水利工程：①**是什么**——新疆吐鲁番的地下引水系统："
     "竖井+暗渠（地下渠道）+明渠+涝坝（蓄水池）四部分；②**为什么在地下**"
     "——吐鲁番极端干旱（年降水约 16 毫米，蒸发量 3000 毫米），地下暗渠"
     "引天山雪水靠重力自流，避免阳光暴晒蒸发——把水「藏」在地下送进绿洲；"
     "③**与长城大运河并称**中国古代三大工程（与都江堰同为古人水智慧）；"
     "④**原理巧思**——利用地形坡度让水自流（无需提水动力），竖井既是"
     "挖掘出土口也是检修通风口；⑤**现状**——全盛时上千条总长五千公里"
     "（「地下运河」），如今仅存数百条仍在使用，2006 年立法保护；⑥"
     "**同类**——伊朗也有同源的坎儿井技术，丝路文明交流的活证。",
     ["坎儿井是什么", "坎儿井怎么工作", "吐鲁番坎儿井",
      "坎儿井为什么不蒸发", "地下运河", "中国古代三大工程"],
     ["问都江堰对比", "问新疆绿洲农业"],
     "atomic", "",
     "坎儿井=吐鲁番地下引水系统竖井+暗渠+明渠+涝坝四部分+地下自流避免"
     "暴晒蒸发(降水16mm蒸发3000mm)+重力自流无需动力竖井兼检修+与长城"
     "大运河并称三大工程+全盛五千公里地下运河+伊朗坎儿井同源丝路活证。"),
]

QUESTIONS = [
    ("QB-1265", "茶马古道是干什么的？为什么高原民族离不开茶叶？", "历史", "技术直答",
     ["茶马", "马帮", "互市", "高原"], "通识拓展342"),
    ("QB-1266", "坎儿井是什么工程？它有什么巧妙之处？", "地理学", "技术直答",
     ["坎儿井", "地下", "暗渠", "蒸发"], "通识拓展342"),
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
                               "level:L2", "status:verified", "batch:通识拓展342"],
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
    bank["version"] = "v6.11"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
