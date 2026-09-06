# -*- coding: utf-8 -*-
"""seed_common_338_cards.py · 通识拓展批次338知识卡+题库（幂等）

338：天文-月食的成因/天文-彗星与哈雷彗星
KCCS 四要素+题干原句触发词。预检已过（QB-1253/1254+双id可用）。
注：日食已有 QB-123，本批取月食与彗星角度避让。
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
    ("kp_card_lunarecl2",
     "月食的成因",
     "天文通识知识点内容（人话接口）", "基础科学",
     "月食是怎么回事：①**原理**——太阳、地球、月亮**恰好排成一条直线**"
     "（地球在中间），月亮进入地球的影子，照不到阳光就「缺」了一块；②"
     "**为什么总在满月**——月食只可能发生在农历十五前后（月亮运行到"
     "地球背日一侧）；③**为什么不是每月都有**——月亮轨道与地球公转轨道"
     "有约 5° 夹角，多数满月时月亮从地影上方或下方「擦过」；④**月全食"
     "「红月亮」**——地球大气把太阳光中的红光折射折射到月面（蓝光被散射"
     "掉），月亮变暗红色——其实是「全地球的日出日落同时照在月亮上」；⑤"
     "**月食 vs 日食**——月食是地球挡住太阳光（半影/本影月食），日食是"
     "月亮挡太阳（只在窄带可见），月食全球夜半球都能看到、持续更长；⑥"
     "**观赏安全**——月食肉眼直接看无伤害（日食需专业滤镜）。",
     ["月食是怎么发生的", "月食为什么在十五", "红月亮是什么",
      "月食和日食的区别", "月全食为什么是红色的", "为什么不是每月都有月食"],
     ["问月食观测", "问行星凌日"],
     "atomic", "",
     "月食=日月地成直线地球居中月入地影+只在满月(农历十五前后)+轨道夹角"
     "5°故非月月有+月全食红月亮=地球大气折射红光(全球日出日落同照月面)"
     "+肉眼安全观赏+月食地球挡光日食月亮挡光。"),
    ("kp_card_halley2",
     "彗星与哈雷彗星",
     "天文通识知识点内容（人话接口）", "基础科学",
     "彗星——太阳系的「脏雪球」：①**构成**——冰、尘埃、岩石与冻结气体"
     "的混合体，靠近太阳时冰升华喷出气体尘埃形成巨大的彗发与彗尾（彗尾"
     "永远背向太阳，被太阳风与光压吹开）；②**哈雷彗星**——约 76 年回归"
     "一次的短周期彗星，1986 年最近一次回归（人类首次探测器近距离观测）"
     "，下次 2061 年；中国古籍对其两千多年连续记载是世界最完整记录；③"
     "**彗星与流星雨**——彗星留下的尘埃碎屑带，地球穿过时碎屑闯入大气"
     "烧蚀成流星雨（每年如期而至的「英仙座」「双子座」流星雨的母体多是"
     "彗星残骸）；④**起源**——太阳系形成时的残留物质（46 亿年「化石」"
     "），多储存在遥远的柯伊伯带与奥尔特云；⑤**撞击史**——1994 年"
     "苏梅克-列维 9 号彗星撞木星（观测史上最壮观的天体撞击）。",
     ["彗星是什么", "哈雷彗星多少年一次", "彗尾为什么背向太阳",
      "彗星和流星雨的关系", "彗星由什么组成", "苏梅克列维9号"],
     ["问小行星带", "问深空探测"],
     "atomic", "",
     "彗星=冰尘埃岩石脏雪球+近日升华喷出彗发彗尾(尾永远背向太阳风压)"
     "+哈雷约76年回归1986近访下次2061+中国古籍两千余年最全记载+彗星"
     "碎屑带=流星雨母体+太阳系46亿年化石居柯伊伯带奥尔特云+SL9撞木星。"),
]

QUESTIONS = [
    ("QB-1253", "月食是怎么发生的？「红月亮」是怎么形成的？", "基础科学", "技术直答",
     ["地球", "影子", "红月亮", "满月"], "通识拓展338"),
    ("QB-1254", "彗星是什么？哈雷彗星多少年回归一次？", "基础科学", "技术直答",
     ["彗星", "哈雷", "76", "回归"], "通识拓展338"),
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
                               "level:L2", "status:verified", "batch:通识拓展338"],
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
    bank["version"] = "v6.07"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
