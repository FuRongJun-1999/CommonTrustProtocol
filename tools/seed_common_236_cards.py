# -*- coding: utf-8 -*-
"""seed_common_236_cards.py · 通识拓展批次236知识卡+题库（幂等）

236：①既有卡补题挂接——kp_card_keju（批次24已写科举卡，当时未出题）补 QB-897
     ②新卡——四大发明-火药（kp_card_firepowder）+ QB-898
KCCS 四要素+题干原句触发词。预检已过（QB-895/896 为批次235所用，本批 QB-897/898）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson"}


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
    ("kp_card_firepowder",
     "火药的发明与应用",
     "人文通识知识点内容（人话接口）", "历史",
     "火药——中国四大发明之一：①**起源**——唐朝炼丹家在炼制「长生丹」时偶然"
     "发现硫磺+硝石+木炭混合物易燃易爆（炼丹术的意外产物，故称「药」），唐代"
     "医药书《真元妙道要略》已警示其危险；②**军事应用**——宋代的火箭/突火枪/"
     "火炮（突火枪是世界最早的管形火器），蒙古西征经阿拉伯人传入欧洲，欧洲"
     "称之「西洋火」，推动骑士城堡时代终结；③**民用**——烟花爆竹/开山采矿/爆竹"
     "驱邪民俗；④**配方本质**——一硫二硝三木炭（硝石提供氧，是氧化剂；硫磺"
     "木炭是燃料），密闭空间点燃急剧膨胀产生爆炸；⑤**文化传播**——阿拉伯语"
     "称硝石为「中国雪」，印证其中国起源。",
     ["火药是谁发明的", "火药是哪个朝代发明的", "火药的主要成分是什么",
      "火药怎么传到欧洲的", "四大发明之火药", "一硫二硝三木炭是什么"],
     ["问现代炸药发展史", "问烟花爆竹燃放法规"],
     "atomic", "",
     "火药=唐炼丹意外发现(硫磺+硝石+木炭/一硫二硝三木炭)→宋军用火箭突火枪"
     "管形火器→经阿拉伯传入欧洲(硝石=中国雪)→民用烟花开山。"),
]

QUESTIONS = [
    ("QB-897", "科举制度是哪个朝代创立的？明清科举乡试、会试、殿试的等级顺序是什么？",
     "历史", "技术直答",
     ["隋", "进士科", "乡试", "会试", "殿试", "举人"], "通识拓展236"),
    ("QB-898", "火药是哪个朝代怎么发明的？主要成分是什么？",
     "历史", "技术直答",
     ["唐", "炼丹", "硫磺", "硝石", "木炭"], "通识拓展236"),
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
                               "level:L2", "status:verified", "batch:通识拓展236"],
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
    bank["version"] = "v5.07"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
