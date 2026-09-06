# -*- coding: utf-8 -*-
"""seed_common_356_cards.py · 通识拓展批次356知识卡+题库（幂等）

356：文物-后母戊鼎/文物-曾侯乙编钟（国宝文物新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1303/1304+双id可用）。
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
    ("kp_card_houmuwu2",
     "后母戊鼎",
     "文物通识知识点内容（人话接口）", "历史",
     "后母戊鼎——世界最大的青铜器：①**基本信息**——商代后期（约前 1300-"
     "1046 年）青铜方鼎，重 832.84 公斤，1939 年河南安阳武官村出土"
     "（村民为防日寇掠夺重新埋回地下，抗战胜利后再挖出）；②**名字**——"
     "鼎腹内壁铭文「后母戊」（旧释「司母戊」），是商王为祭祀母亲「戊」"
     "所铸；③**铸造技术**——需上千公斤金属液同时浇铸，多人协作多组陶范"
     "（复合范铸造法），合金配比铜锡铅合理，反映商代青铜冶铸巅峰；④**"
     "纹饰**——兽面纹（饕餮纹）庄严神秘，鼎耳饰双虎食人首纹；⑤**地位**"
     "——现存最重单体青铜器，「镇国之宝」，藏中国国家博物馆，禁止出境"
     "展览文物。",
     ["后母戊鼎是谁的", "后母戊鼎有多重", "司母戊鼎改名",
      "世界最大的青铜器", "后母戊鼎出土", "饕餮纹"],
     ["问四羊方尊", "问青铜铸造工艺"],
     "atomic", "",
     "后母戊鼎=商后期青铜方鼎832.84kg世界最重单体青铜器+1939安阳武官村"
     "出土防日寇掠夺重埋+铭文后母戊商王祭母+复合范铸造千人协作合金配比"
     "合理+兽面纹鼎耳双虎食人首+国博藏禁止出境展览。"),
    ("kp_card_zenghouyibells",
     "曾侯乙编钟",
     "文物通识知识点内容（人话接口）", "历史",
     "曾侯乙编钟——地下音乐厅的千年绝响：①**出土**——1978 年湖北随州"
     "曾侯乙墓（战国早期约前 433 年），65 件编钟分三层八组悬挂于钟架"
     "（总重 2.5 吨，至今仍稳立原位）；②**一钟双音**——每件钟正鼓侧鼓"
     "可敲出相差三度的两个乐音（合瓦形钟体设计），世界音乐史奇迹；③**"
     "音域**——跨五个半八度，十二个半音齐备，可旋宫转调演奏中外乐曲"
     "（曾演奏《东方红》）；④**铭文**——钟体 3700 余字铭文记录先秦乐律"
     "理论（失传的音乐教科书）；⑤**铸造**——范铸+失蜡法浑然一体，反映"
     "战国青铜铸造与声学最高水平；⑥**现状**——藏湖北省博物馆，复制件"
     "常演奏，原件演奏仅三次（每次都在损耗）。",
     ["曾侯乙编钟", "编钟是干什么用的", "一钟双音",
      "曾侯乙编钟出土", "编钟铭文", "战国青铜器"],
     ["问中国古代乐器", "问礼乐制度"],
     "atomic", "",
     "曾侯乙编钟=1978湖北随州战国早期曾侯乙墓出土+65件三层八组2.5吨"
     "+一钟双音合瓦形设计世界音乐史奇迹+音域五个半八度十二半音齐备"
     "+3700字铭文记录失传乐律+范铸失蜡法巅峰+原件演奏仅三次藏湖北省博。"),
]

QUESTIONS = [
    ("QB-1303", "后母戊鼎出土于哪里？它为什么珍贵？", "历史", "技术直答",
     ["安阳", "商代", "832", "世界最重"], "通识拓展356"),
    ("QB-1304", "曾侯乙编钟是哪里出土的？「一钟双音」是什么意思？", "历史", "技术直答",
     ["曾侯乙", "编钟", "双音", "战国"], "通识拓展356"),
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
                               "level:L2", "status:verified", "batch:通识拓展356"],
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
    bank["version"] = "v6.22"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
