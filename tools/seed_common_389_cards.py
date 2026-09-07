# -*- coding: utf-8 -*-
"""seed_common_389_cards.py · 通识拓展批次389知识卡+题库（幂等）

389：1 张存量卡补题（露水角度→云雾形成 kp_card_cloudfog，已在库）
    + 2 张新卡（冰雹 kp_card_hail / 瀑布 kp_card_waterfall）。
KCCS 四要素+题干原句触发词。预检已过（QB-1405~1407 可用，
露水/冰雹/瀑布题库 0 覆盖；微波炉已有 QB-148/767 排除）。
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
    ("kp_card_hail",
     "冰雹",
     "气象常识知识点内容（人话接口）", "自然常识",
     "冰雹——从强雷雨云中掉下的冰疙瘩：①**怎么形成**——春夏的强对流"
     "天气里，积雨云内上升气流猛烈，水滴被托到高空冻结成小冰核；冰核"
     "在云中反复升降，每过一层湿气区就裹一层冰，像滚雪球一样越长越大，"
     "直到气流托不住才砸到地面；②**多发时间**——春夏之交和夏季午后"
     "（地面受热强、对流最旺的时段），范围小、历时短但破坏力集中；③**"
     "危害与防御**——砸坏庄稼、车辆、温室大棚，大冰雹伤人；收到预警"
     "尽快进室内，户外用包/衣物护住头，车辆停进车库或地下停车场；④**"
     "辨析**——直径 5 毫米以上才叫冰雹，更小的冰粒叫冰丸；冰雹是硬冰"
     "块，霰（软雹）松软一捏就碎。",
     ["冰雹是怎么形成的", "冰雹多发在什么季节", "冰雹来了怎么办",
      "冰雹和冰丸区别", "为什么夏天 下冰雹", "冰雹预警"],
     ["问台风", "问雷电防护"],
     "atomic", "",
     "冰雹=强对流积雨云中水滴被上升气流托到高空冻结成核反复升降裹冰"
     "层滚大掉落+春夏之交夏季午后多发范围小破坏集中+预警进室内护头车"
     "停车库+直径5毫米以上才叫冰雹小冰粒叫冰丸+冰雹硬霰软一捏碎。"),
    ("kp_card_waterfall",
     "瀑布",
     "地理常识知识点内容（人话接口）", "自然常识",
     "瀑布——河流遇到陡坎跌水而下的景观：①**怎么形成**——最常见是"
     "「差异侵蚀」：河床由软硬不同的岩层叠成，软岩被水流掏空冲走，硬"
     "岩凸出形成陡坎，水从坎上跌落成瀑布；断层错动、冰川刨蚀也能造出"
     "落差；②**著名瀑布**——黄果树瀑布（贵州，中国最大水量的瀑布之一"
     "，水帘洞可从瀑布后穿行）、尼亚加拉瀑布（美国加拿大边界）、伊瓜苏"
     "瀑布（南美，最宽之一）、维多利亚瀑布（非洲）；③**诗句**——李白"
     "「飞流直下三千尺，疑是银河落九天」写庐山瀑布；④**瀑布会后退**——"
     "跌水不断掏蚀坎底，硬岩层悬空崩塌，瀑布位置逐年向上游退移；⑤**"
     "提示**——瀑布区水雾大，雨具防潮，观景走指定栈道。",
     ["瀑布是怎么形成的", "黄果树瀑布在哪里", "世界著名瀑布",
      "瀑布为什么会后退", "飞流直下三千尺", "差异侵蚀"],
     ["问峡谷", "问喀斯特地貌"],
     "atomic", "",
     "瀑布=软硬岩层差异侵蚀软岩掏空硬岩成坎跌水+断层冰川也可造落差+"
     "黄果树中国最大尼亚加拉伊瓜苏维多利亚世界著名+李白飞流直下三千尺"
     "庐山+跌水掏蚀坎底悬空崩塌位置向上游退+水雾大雨具走栈道。"),
]

QUESTIONS = [
    ("QB-1405", "露水是怎么形成的？它和霜有什么区别？",
     "自然常识", "技术直答",
     ["露水", "液化", "水蒸气", "凝结"], "通识拓展389·存量卡补题"),
    ("QB-1406", "冰雹是怎么形成的？为什么多发生在夏天？",
     "自然常识", "技术直答",
     ["冰雹", "强对流", "上升气流", "夏天"], "通识拓展389"),
    ("QB-1407", "瀑布是怎么形成的？中国最大的瀑布在哪里？",
     "地理常识", "技术直答",
     ["瀑布", "侵蚀", "黄果树", "落差"], "通识拓展389"),
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
                               "level:L2", "status:verified", "batch:通识拓展389"],
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
    bank["version"] = "v6.59"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
