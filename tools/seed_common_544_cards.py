# -*- coding: utf-8 -*-
"""seed_common_544_cards.py · 通识拓展批次544知识卡+题库（幂等）

544：2 张新卡·纸品旧藏域（火花收藏 kp_card_huohua /
    老课本收藏 kp_card_laokb——id 与语义等价卡名双重确认双零）。
预检已过（QB-1864~1866 可用）。
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
    ("kp_card_huohua",
     "火花收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "火花收藏——火柴盒上的微缩美术馆：①**什么是火花**——火柴盒上的"
     "贴画商标，与邮票并称收藏界「姊妹花」，收藏者谓之「集花」；②**起"
     "源**——中国最早的民族火柴厂之一广东巧明火柴厂（1879 年），其「舞"
     "龙牌」贴画被视为早期火花名品；③**内容百花齐放**——名胜古迹、戏"
     "曲人物、花鸟鱼虫、广告商标，方寸纸片浓缩百年商业美术史；④**名厂"
     "名品**——天津、上海、广州等老火柴厂的成套火花最受追捧；⑤**意义"
     "**——电子打火时代火柴渐退，火花成为「熄灭的记忆」的收藏载体。",
     ["火花收藏", "火柴盒贴画", "姊妹花", "巧明火柴厂",
      "舞龙牌", "集花"],
     ["问集邮", "问老物件收藏"],
     "atomic", "",
     "火花收藏=火柴盒贴画商标与邮票姊妹花集花+巧明火柴厂1879舞龙牌早"
     "期名品+名胜戏曲花鸟广告浓缩百年商业美术史+津沪穗老厂成套受捧+电"
     "子打火时代熄灭的记忆载体。"),
    ("kp_card_laokb",
     "老课本收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "老课本收藏——旧课本里的教育初心：①**民国老课本**——叶圣陶编、"
     "丰子恺绘的《开明国语课本》（1932）语句浅白有爱，近年再版走红；"
     "②**商务印书馆**——1897 年创于上海，中国现代出版业开端，其《最新"
     "国文教科书》影响深远；③**承上**——老课本上承蒙学传统（《三字经"
     "》《百家姓》），下启现代国民教育；④**收藏看点**——版本（初版最"
     "贵）、品相、名家编绘与插图；⑤**意义**——老课本是一面镜子：教育"
     "理念、语言变迁、时代审美皆在其中。",
     ["老课本收藏", "开明国语课本", "丰子恺", "叶圣陶",
      "商务印书馆", "最新国文教科书"],
     ["问善本收藏", "问连环画收藏"],
     "atomic", "",
     "老课本收藏=开明国语课本1932叶圣陶编丰子恺绘浅白有爱再版走红+商"
     "务印书馆1897上海现代出版开端最新国文教科书+上承蒙学三字经下启国"
     "民教育+收藏看版本品相名家编绘+教育理念语言变迁时代审美的镜子。"),
]

QUESTIONS = [
    ("QB-1864", "收藏界的「火花」指什么？它和邮票是什么关系？",
     "传统文化", "技术直答",
     ["火花", "火柴盒", "贴画", "邮票"], "通识拓展544·新卡"),
    ("QB-1865", "中国早期著名火柴厂和火花名品有哪些？",
     "传统文化", "技术直答",
     ["巧明火柴厂", "舞龙牌", "火花", "火柴厂"], "通识拓展544·新卡"),
    ("QB-1866", "《开明国语课本》是谁编绘的？为什么广受好评？",
     "传统文化", "技术直答",
     ["开明国语课本", "叶圣陶", "丰子恺", "老课本"], "通识拓展544·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展544"],
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
    bank["version"] = "v8.09"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
