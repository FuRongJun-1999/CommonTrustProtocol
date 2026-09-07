# -*- coding: utf-8 -*-
"""seed_common_511_cards.py · 通识拓展批次511知识卡+题库（幂等）

511：2 张新卡·文字乐器域（仓颉造字 kp_card_cangjie /
    民族乐器撷英 kp_card_minzuyueqi——按卡名精确确认无独立卡；
    编钟 kp_card_zenghouyibells 已有专卡跳过）。
预检已过（QB-1765~1767 可用）。
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
    ("kp_card_cangjie",
     "仓颉造字",
     "文字起源知识点内容（人话接口）", "历史与文明",
     "仓颉造字——汉字起源的传说与史实：①**传说**——仓颉是黄帝的史官"
     "，生有四目，观察鸟兽足迹、山川形状而创造文字，《淮南子》载造字"
     "时「天雨粟，鬼夜哭」——文字一出，天机泄露；②**史实**——考古表"
     "明甲骨文（商代晚期）已是成熟文字体系，此前必有漫长演进（各地刻"
     "符），文字不可能由一人一时独创；③**合理解读**——仓颉更可能是整"
     "理、规范文字的史官群体象征（鲁迅：仓颉不止一个）；④**识字启蒙"
     "**——传统蒙学把仓颉奉为「文字之神」，有仓颉庙（陕西白水）；⑤**"
     "精神**——传说承载的是先民对文字创造者的敬意：一字一世界，敬惜"
     "字纸。",
     ["仓颉造字的故事", "仓颉是谁", "汉字是谁发明的",
      "天雨粟鬼夜哭", "文字起源", "甲骨文之前有文字吗"],
     ["问汉字六书", "问甲骨文"],
     "atomic", "",
     "仓颉造字=黄帝史官四目观鸟兽迹造字传说淮南子天雨粟鬼夜哭+甲骨文"
     "商晚期已成熟必有漫长演进不可能一人独创+仓颉是整理规范文字的史官"
     "群体象征+陕西白水仓颉庙文字之神+传说承载先民对文字创造的敬意"
     "。"),
    ("kp_card_minzuyueqi",
     "民族乐器撷英",
     "音乐常识知识点内容（人话接口）", "艺术学堂",
     "民族乐器撷英——最有故事的中国乐器：①**古琴**——七弦琴（传说周"
     "文王武王各加一弦），2003 年「古琴艺术」入选人类非物质文化遗产"
     "，《高山流水》伯牙子期「知音」典故、《广陵散》嵇康绝响；②**琵琶"
     "**——四弦，曲项琵琶自西域传入，白居易《琵琶行》「大珠小珠落玉"
     "盘」，武曲《十面埋伏》模拟楚汉垓下之战；③**二胡**——两弦，源自"
     "唐代奚琴，阿炳（华彦钧）《二泉映月》如泣如诉，指挥家小泽征尔感"
     "叹「应跪着听」；④**笛箫**——竹制横吹为笛、竖吹为箫，「谁家玉笛"
     "暗飞声」；⑤**编钟**——先秦青铜打击乐巅峰（详见曾侯乙编钟卡）"
     "；八音分类：金石土革丝木匏竹。",
     ["古琴有几根弦", "高山流水遇知音", "琵琶行大珠小珠",
      "二泉映月是谁", "二胡几根弦", "民族乐器"],
     ["问编钟", "问十二平均律"],
     "atomic", "",
     "民族乐器=古琴七弦2003年人类非遗高山流水知音广陵散绝响+琵琶四弦"
     "西域传入琵琶行大珠小珠十面埋伏+二胡两弦源自奚琴阿炳二泉映月+笛"
     "横吹箫竖吹+编钟青铜八音金石土革丝木匏竹。"),
]

QUESTIONS = [
    ("QB-1765", "仓颉造字是真实历史吗？「天雨粟，鬼夜哭」是什么意思？",
     "历史常识", "技术直答",
     ["仓颉", "造字", "天雨粟", "传说"], "通识拓展511·新卡"),
    ("QB-1766", "「高山流水遇知音」讲的是谁？古琴有几根弦？",
     "音乐常识", "技术直答",
     ["高山流水", "伯牙", "子期", "古琴"], "通识拓展511·新卡"),
    ("QB-1767", "《二泉映月》是谁的作品？二胡有几根弦？",
     "音乐常识", "技术直答",
     ["二泉映月", "阿炳", "二胡", "两弦"], "通识拓展511·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展511"],
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
    bank["version"] = "v7.76"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
