# -*- coding: utf-8 -*-
"""seed_common_508_cards.py · 通识拓展批次508知识卡+题库（幂等）

508：2 张新卡·典故神话域（典故成语四则 kp_card_chengyugushi /
    希腊罗马神话对照 kp_card_greekroman）。
预检已过（QB-1756~1758 可用，两主题按卡名精确确认双零）。
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
    ("kp_card_chengyugushi",
     "典故成语四则",
     "成语典故知识点内容（人话接口）", "艺术学堂",
     "典故成语四则——耳熟能详的经典故事：①**画龙点睛**——南朝梁画家"
     "张僧繇在金陵安乐寺画四龙不点睛，称「点睛即飞去」，众人不信，刚"
     "点两龙即破壁飞走——比喻在关键处一笔点明要旨，全篇生辉；②**画"
     "蛇添足**——《战国策·齐策》门客们约定先画完蛇者得酒，一人先画"
     "完却添上脚，蛇失其真，酒也没喝上——比喻多此一举反而坏事；③**杯"
     "弓蛇影**——晋人乐广待客，客人见酒杯里有「蛇」（实为墙上弓的倒"
     "影）喝下后疑惧成病，乐广点破真相病愈——比喻疑神疑鬼、自相惊扰"
     "；④**望梅止渴**——《世说新语》载曹操行军缺水，谎称前方有梅林"
     "，士兵口舌生津暂解干渴——比喻以空想安慰自己。",
     ["画龙点睛的典故", "张僧繇", "画蛇添足出自哪", "杯弓蛇影什么意思",
      "望梅止渴是谁", "成语典故故事"],
     ["问守株待兔", "问成语来源"],
     "atomic", "",
     "典故成语四则=画龙点睛南朝张僧繇金陵安乐寺点睛破壁飞去关键点睛+"
     "画蛇添足战国策齐策先画完添脚失酒多此一举+杯弓蛇影晋乐广墙上弓"
     "倒影疑惧成病点破自相惊扰+望梅止渴世说新语曹操谎称梅林生津空想"
     "自慰。"),
    ("kp_card_greekroman",
     "希腊罗马神话对照",
     "神话文学知识点内容（人话接口）", "艺术学堂",
     "希腊罗马神话对照——同一神系两个名字：①**对应关系**——罗马神话"
     "基本继承希腊神系只是改名：宙斯→朱庇特（众神之王）、赫拉→朱诺、"
     "雅典娜→密涅瓦（智慧女神）、阿佛洛狄忒→维纳斯（爱与美）、阿瑞"
     "斯→玛尔斯（战争）、波塞冬→尼普顿（海）、赫尔墨斯→墨丘利（信"
     "使）、阿尔忒弥斯→狄安娜（月亮狩猎）、厄洛斯→丘比特（小爱神，"
     "金箭）；②**行星与月份**——太阳系行星多用罗马名：水星墨丘利、"
     "金星维纳斯、火星玛尔斯、木星朱庇特、海王星尼普顿；英语六月之"
     "名源自朱诺；③**文化印记**——「丘比特之箭」「维纳斯雕像」「密涅瓦"
     "的猫头鹰」等意象都源自罗马名；④**辨析技巧**——看语境：文学艺"
     "术圈常混用，天文学一律罗马名，读希腊原著则希腊名。",
     ["宙斯的罗马名字", "维纳斯是谁的罗马名", "朱庇特和宙斯",
      "丘比特是谁", "密涅瓦", "希腊罗马神对应"],
     ["问希腊神话", "问北欧神话"],
     "atomic", "",
     "希腊罗马神话对照=宙斯朱庇特赫拉朱诺雅典娜密涅瓦阿佛洛狄忒维纳"
     "斯阿瑞斯玛尔斯波塞冬尼普顿赫尔墨斯墨丘利阿尔忒弥斯狄安娜厄洛斯"
     "丘比特+行星多用罗马名水星金星火星木星海王星+六月源自朱诺+罗马"
     "继承希腊神系改名文学混用天文一律罗马名。"),
]

QUESTIONS = [
    ("QB-1756", "「画龙点睛」的典故是什么？和哪位画家有关？",
     "文学常识", "技术直答",
     ["画龙点睛", "张僧繇", "典故", "安乐寺"], "通识拓展508·新卡"),
    ("QB-1757", "「杯弓蛇影」和「望梅止渴」分别是什么意思？",
     "文学常识", "技术直答",
     ["杯弓蛇影", "望梅止渴", "乐广", "曹操"], "通识拓展508·新卡"),
    ("QB-1758", "宙斯和朱庇特是什么关系？维纳斯对应希腊哪位神？",
     "文学常识", "技术直答",
     ["宙斯", "朱庇特", "维纳斯", "阿佛洛狄忒"], "通识拓展508·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展508"],
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
    bank["version"] = "v7.73"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
