# -*- coding: utf-8 -*-
"""seed_common_546_cards.py · 通识拓展批次546知识卡+题库（幂等）

546：2 张新卡·纸艺收藏域（糖纸收藏 kp_card_tangzhi /
    剪纸流派 kp_card_jianzhi——id 与语义等价卡名双重确认；
    剪纸刻法寓意 QB-984 已覆盖，本批立流派非遗角度新卡不重复）。
预检已过（QB-1870~1872 可用）。
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
    ("kp_card_tangzhi",
     "糖纸收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "糖纸收藏——甜味的时代记忆：①**是什么**——糖果包装纸：七八十年代"
     "物质匮乏，一张花花绿绿的糖纸是孩子的珍宝，抚平了夹在书页里攒着"
     "；②**种类**——玻璃糖纸（透明脆亮印彩色图案）、蜡光糖纸、铝箔糖"
     "纸；③**名厂记忆**——上海冠生园（大白兔奶糖）、北京义利等国营糖"
     "果厂的糖纸承载几代人的甜；④**玩法**——比谁攒得多、攒得全，向同"
     "伴炫耀「收藏册」；⑤**如今**——糖纸已成怀旧收藏品，成套的国产老"
     "糖纸在旧货市场颇受追捧，收藏的是甜也是童年。",
     ["糖纸收藏", "玻璃糖纸", "冠生园", "大白兔",
      "怀旧收藏", "糖纸"],
     ["问老物件收藏", "问火花收藏"],
     "atomic", "",
     "糖纸收藏=糖果包装纸七八十年代孩子珍宝抚平夹书攒着+玻璃糖纸透明"
     "脆亮蜡光铝箔+冠生园大白兔义利国营厂几代人的甜+比攒得多全收藏册"
     "炫耀+怀旧收藏成套老糖纸追捧收藏甜与童年。"),
    ("kp_card_jianzhi",
     "剪纸流派",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "剪纸流派——一把剪刀剪出南北风情：①**源流**——纸出现后剪纸随之"
     "而生，新疆吐鲁番出土的北朝团花剪纸是现存最早的剪纸实物；②**北方"
     "流派**——陕西安塞剪纸粗犷质朴「生命之花」，河北蔚县剪纸以染色点"
     "彩独树一帜（先刻后染）；③**南方流派**——扬州剪纸线条清秀如工笔"
     "，佛山剪纸以铜凿金碧辉煌；④**用途**——窗花、喜花、礼花、绣样，"
     "节庆婚嫁无所不在；⑤**地位**——2009 年中国剪纸入选联合国人类非物"
     "质文化遗产代表作名录。",
     ["剪纸流派", "安塞剪纸", "蔚县剪纸", "扬州剪纸",
      "佛山剪纸", "剪纸非遗"],
     ["问木版年画", "问剪纸刻法"],
     "atomic", "",
     "剪纸流派=新疆吐鲁番北朝团花现存最早实物+北方安塞粗犷质朴蔚县染色"
     "点彩先刻后染+南方扬州清秀工笔佛山铜凿金碧辉煌+窗花喜花礼花绣样节"
     "庆婚嫁+2009中国剪纸人类非遗代表作名录。"),
]

QUESTIONS = [
    ("QB-1870", "糖纸为什么成了收藏品？玻璃糖纸是什么？",
     "传统文化", "技术直答",
     ["糖纸", "玻璃糖纸", "怀旧", "收藏"], "通识拓展546·新卡"),
    ("QB-1871", "剪纸有哪些南北流派？各有什么特点？",
     "传统文化", "技术直答",
     ["剪纸流派", "安塞", "蔚县", "扬州"], "通识拓展546·新卡"),
    ("QB-1872", "中国剪纸入选非遗是什么时候？现存最早的剪纸实物在哪里？",
     "传统文化", "技术直答",
     ["剪纸", "非遗", "2009", "北朝团花"], "通识拓展546·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展546"],
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
    bank["version"] = "v8.11"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
