# -*- coding: utf-8 -*-
"""seed_common_566_cards.py · 通识拓展批次566知识卡+题库（幂等）

566：2 张新卡·床榻农谚域（床榻谱系 kp_card_chuangta /
    农谚智慧 kp_card_nongyan——id 与语义等价卡名双重确认双零）。
预检已过（QB-1930~1932 可用）。
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
    ("kp_card_chuangta",
     "床榻谱系",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "床榻谱系——古人的卧具讲究：①**榻**——窄而矮，坐卧两用；「下榻"
     "」典故：东汉陈蕃为高士徐稚特设一榻，去则悬之——留宿贵客叫下榻；"
     "②**罗汉床**——三面围子，可坐可卧，待客小憩两相宜；③**架子床**"
     "——四柱床架可挂帐幔；④**拔步床**——明清大户嫁妆重器：床前带浅"
     "廊小平台，如屋中屋；⑤**贵妃榻**——美人小憩的贵妃榻；⑥**争议"
     "考点**——李白「床前明月光」的「床」一说为可折叠的胡床（坐具），"
     "亦有井栏说，学界至今有讨论。",
     ["床榻", "罗汉床", "拔步床", "架子床",
      "下榻的典故", "床前明月光的床"],
     ["问明式家具", "问吉祥图案"],
     "atomic", "",
     "床榻谱系=榻窄矮坐卧两用下榻典故陈蕃徐稚去则悬之+罗汉床三面围子待"
     "客小憩+架子床四柱挂帐+拔步床明清嫁妆重器床前浅廊屋中屋+贵妃榻+"
     "床前明月光床为胡床井栏说学界有讨论。"),
    ("kp_card_nongyan",
     "农谚智慧",
     "民俗知识点内容（人话接口）", "传统文化",
     "农谚智慧——田野里的天气与农时预报：①**瑞雪兆丰年**——厚雪给越"
     "冬作物保温、冻死害虫、融雪增墒，故冬雪多是丰年吉兆；②**农时**——"
     "「清明前后，种瓜点豆」——按节气安排播种；③**看天**——「朝霞不"
     "出门，晚霞行千里」「蚂蚁搬家蛇过道，大雨不久要来到」——物候观测"
     "的朴素经验；④**价值**——农谚是千年观察的经验库，虽有地域局限，"
     "却是古代农业社会的「大数据」；⑤**今用**——许多谚语与现代气象学"
     "原理暗合，可作科普桥梁。",
     ["农谚", "瑞雪兆丰年", "清明前后种瓜点豆",
      "朝霞不出门", "蚂蚁搬家蛇过道", "农时"],
     ["问二十四节气", "问数九与三伏"],
     "atomic", "",
     "农谚智慧=瑞雪兆丰年保温冻虫增墒丰年吉兆+清明前后种瓜点豆按节气播"
     "种+朝霞不出门晚霞行千里蚂蚁搬家蛇过道大雨不久物候经验+千年观察经"
     "验库地域局限古代大数据+与现代气象学暗合科普桥梁。"),
]

QUESTIONS = [
    ("QB-1930", "「下榻」这个词有什么典故？罗汉床是做什么用的？",
     "传统文化", "技术直答",
     ["下榻", "罗汉床", "陈蕃", "榻"], "通识拓展566·新卡"),
    ("QB-1931", "拔步床是什么？为什么说是大户人家的嫁妆重器？",
     "传统文化", "技术直答",
     ["拔步床", "嫁妆", "明清", "床中床"], "通识拓展566·新卡"),
    ("QB-1932", "「瑞雪兆丰年」有科学道理吗？还有哪些农谚？",
     "传统文化", "技术直答",
     ["瑞雪兆丰年", "农谚", "积雪", "墒情"], "通识拓展566·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展566"],
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
    bank["version"] = "v8.31"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
