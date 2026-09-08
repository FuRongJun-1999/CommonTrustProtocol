# -*- coding: utf-8 -*-
"""seed_common_572_cards.py · 通识拓展批次572知识卡+题库（幂等）

572：2 张新卡·影像竹刻域（老照片收藏 kp_card_laopian /
    留青竹刻与扇骨 kp_card_shangu——id 与语义等价卡名双重确认双零）。
预检已过（QB-1948~1950 可用）。
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
    ("kp_card_laopian",
     "老照片收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "老照片收藏——定格时光的银盐记忆：①**摄影术传入**——1839 年达盖"
     "尔法公布后，摄影术在清晚期经广州、香港传入中国；②**早期照相馆**"
     "——上海、北京、广州涌现照相馆，北京丰泰照相馆 1905 年拍摄京剧"
     "《定军山》片段——中国人自己摄制的第一部电影；③**收藏看点**——"
     "原版与翻印（银盐纸基质感）、时代信息（服饰、建筑、街景）、名人"
     "影像与签名；④**保护**——避光防潮、用无酸卡纸装裱、忌手指触药膜"
     "面；⑤**意义**——老照片是最直观的史料，一帧影像胜千言。",
     ["老照片收藏", "照相馆", "丰泰照相馆", "定军山",
      "银盐", "原版"],
     ["问古玩行话", "问集邮"],
     "atomic", "",
     "老照片收藏=1839达盖尔法公布清晚期经广州香港传入+早期照相馆上海"
     "北京广州+丰泰照相馆1905定军山中国自己摄制第一部电影+原版翻印银盐"
     "纸基时代信息名人影像+避光防潮无酸装裱一帧胜千言。"),
    ("kp_card_shangu",
     "留青竹刻与扇骨",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "留青竹刻与扇骨——竹上生花的微雕功夫：①**留青竹刻**——以竹皮"
     "（竹青）为「墨」：铲去图层外的竹青留住纹样，竹青久转深黄、竹肌"
     "渐显深褐，层次如水墨；常州留青竹刻列入国家级非遗；②**竹刻重镇**"
     "——明清嘉定竹刻（朱鹤祖孙三代开创深浮雕传统）是竹刻艺术的高峰"
     "；③**扇骨收藏**——折扇扇骨材质有竹木牙角，名家刻扇（书画上骨）"
     "一骨难求；④**上手**——竹刻怕燥裂，宜常摩挲养浆；扇骨展开收拢"
     "要轻，防断篾。",
     ["留青竹刻", "扇骨", "常州竹刻", "嘉定竹刻",
      "竹青", "刻扇"],
     ["问扇子文化", "问玉器雕工"],
     "atomic", "",
     "留青竹刻扇骨=竹皮竹青为墨铲青留纹竹青转黄竹肌深褐层次如水墨+常"
     "州留青竹刻国家级非遗+明清嘉定竹刻朱氏三代深浮雕高峰+扇骨竹木牙角"
     "名家刻扇一骨难求+怕燥裂常摩挲养浆轻展防断篾。"),
]

QUESTIONS = [
    ("QB-1948", "中国人自己摄制的第一部电影出自哪里？和照相馆有什么关系？",
     "历史常识", "技术直答",
     ["丰泰照相馆", "定军山", "第一部电影", "北京"], "通识拓展572·新卡"),
    ("QB-1949", "老照片收藏要注意什么？怎么判断是不是原版？",
     "传统文化", "技术直答",
     ["老照片", "原版", "银盐", "收藏"], "通识拓展572·新卡"),
    ("QB-1950", "留青竹刻「留」的是什么？常州竹刻有什么地位？",
     "传统文化", "技术直答",
     ["留青竹刻", "竹青", "常州", "非遗"], "通识拓展572·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展572"],
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
    bank["version"] = "v8.37"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
