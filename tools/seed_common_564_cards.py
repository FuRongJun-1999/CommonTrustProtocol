# -*- coding: utf-8 -*-
"""seed_common_564_cards.py · 通识拓展批次564知识卡+题库（幂等）

564：2 张新卡·吉祥寓意域（吉祥图案 kp_card_jixiang /
    花中四君子 kp_card_sijunzi——id 与语义等价卡名双重确认双零；
    蝙蝠 QB-929 为动物题，吉祥谐音角度不重复）。
预检已过（QB-1924~1926 可用）。
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
    ("kp_card_jixiang",
     "吉祥图案",
     "传统艺术知识点内容（人话接口）", "传统文化",
     "吉祥图案——藏在纹样里的祝福：①**谐音法**——蝙蝠谐「遍福」（倒"
     "挂蝙蝠=「福到」）、鹿谐「禄」、鱼谐「余」（莲与鱼=「连年有余」）、"
     "瓶谐「平」（瓶插月季=「四季平安」）、喜鹊登梅=「喜上眉梢」；②**"
     "象征法**——五只蝙蝠围寿字=「五福捧寿」（寿、富、康宁、好德、善"
     "终），三只羊=「三阳开泰」（冬去春来），猴骑马=「马上封侯」，瓜"
     "瓞绵绵喻子孙昌盛；③**组合法**——多种吉祥物组合成图：龙凤呈祥、"
     "松鹤延年、鸳鸯戏水（婚庆）；④**应用**——年画、瓷器、家具雕花、"
     "织绣、建筑砖雕处处可见；⑤**意义**——谐音+象征的视觉语言，是把"
     "好日子「画」出来的民间智慧。",
     ["吉祥图案", "蝙蝠福到", "连年有余", "喜上眉梢",
      "五福捧寿", "三阳开泰"],
     ["问剪纸流派", "问年画"],
     "atomic", "",
     "吉祥图案=谐音法蝙蝠遍福倒挂福到鹿禄鱼余连年有余瓶平喜鹊登梅喜上"
     "眉梢+象征法五蝠捧寿寿富康宁好德善终三羊三阳开泰猴骑马马上封侯瓜"
     "瓞绵绵+组合法龙凤呈祥松鹤延年鸳鸯戏水+年画瓷器家具织绣砖雕处处"
     "可见+谐音象征视觉语言画出来的祝福。"),
    ("kp_card_sijunzi",
     "花中四君子",
     "传统文化知识点内容（人话接口）", "传统文化",
     "花中四君子——梅兰竹菊的人格投射：①**梅**——凌寒独自开，傲雪"
     "风骨（「梅花香自苦寒来」）；②**兰**——空谷幽兰，幽香隐逸，君子"
     "慎独；③**竹**——虚心有节，宁折不弯（郑板桥画竹）；④**菊**——"
     "傲霜隐逸，陶渊明「采菊东篱下，悠然见南山」；⑤**由来**——明代"
     "黄凤池辑《梅竹兰菊四谱》而定名；⑥**近亲**——「岁寒三友」松、"
     "竹、梅（取《论语》岁寒松柏之意），常与四君子同入画题；⑦**意义**"
     "——把植物当人格镜子，是中国艺术「托物言志」的代表。",
     ["花中四君子", "梅兰竹菊", "岁寒三友", "郑板桥",
      "陶渊明", "托物言志"],
     ["问陶渊明", "问吉祥图案"],
     "atomic", "",
     "四君子=梅凌寒傲雪兰花自苦寒来+兰空谷幽香君子慎独+竹虚心有节宁折"
     "不弯郑板桥画竹+菊傲霜隐逸采菊东篱下+明代黄凤池梅竹兰菊四谱定名+"
     "岁寒三友松竹梅+托物言志人格镜子。"),
]

QUESTIONS = [
    ("QB-1924", "蝙蝠倒挂为什么寓意「福到」？还有哪些谐音吉祥图案？",
     "传统文化", "技术直答",
     ["吉祥图案", "蝙蝠", "谐音", "连年有余"], "通识拓展564·新卡"),
    ("QB-1925", "「花中四君子」是哪四种植物？各象征什么品格？",
     "传统文化", "技术直答",
     ["花中四君子", "梅兰竹菊", "品格", "象征"], "通识拓展564·新卡"),
    ("QB-1926", "「岁寒三友」指哪三种植物？出自什么典故？",
     "传统文化", "技术直答",
     ["岁寒三友", "松竹梅", "典故", "傲霜"], "通识拓展564·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展564"],
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
    bank["version"] = "v8.29"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
