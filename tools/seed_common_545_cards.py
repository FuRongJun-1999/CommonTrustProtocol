# -*- coding: utf-8 -*-
"""seed_common_545_cards.py · 通识拓展批次545知识卡+题库（幂等）

545：1 张新卡·广告纸品域（月份牌与烟画 kp_card_yuefenpai——
    id 与语义等价卡名双重确认双零；木版年画 kp_card_nianhua2
    已有卡查重跳过）。
预检已过（QB-1867~1869 可用）。
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
    ("kp_card_yuefenpai",
     "月份牌与烟画",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "月份牌与烟画——老上海的纸片摩登：①**月份牌**——20 世纪上半叶上"
     "海流行的商业广告画，因附印年历得名；擦笔水彩技法（炭精打底晕染）"
     "画出丰腴柔美的旗袍仕女，是老上海的视觉名片；②**月份牌名家**——"
     "杭稚英（稚英画室）、金梅生、谢之光等，客户多为烟草、布匹、医药商"
     "号；③**烟画**——香烟盒内附赠的小画片，约名片大小，题材包罗戏曲"
     "名伶、小说人物、花鸟鱼虫，集齐整套可换奖——最早的「集换式卡牌"
     "」营销；④**地位**——月份牌、烟画与邮票、火花并列，是纸片收藏的"
     "重要门类；⑤**意义**——一张纸片记录洋货入侵、商战、时尚与市民审"
     "美的百年变迁。",
     ["月份牌", "烟画", "杭稚英", "金梅生", "擦笔水彩",
      "香烟画片"],
     ["问火花收藏", "问老物件收藏"],
     "atomic", "",
     "月份牌烟画=月份牌20世纪上海商业广告画附年历得名擦笔水彩旗袍仕女"
     "老上海视觉名片+杭稚英稚英画室金梅生谢之光名家+烟画香烟盒附赠名片"
     "大小题材包罗集齐换奖最早集换式卡牌营销+与邮票火花并列纸片收藏+记"
     "录商战时尚市民审美百年变迁。"),
]

QUESTIONS = [
    ("QB-1867", "「月份牌」是什么？为什么叫这个名字？",
     "传统文化", "技术直答",
     ["月份牌", "广告画", "年历", "上海"], "通识拓展545·新卡"),
    ("QB-1868", "月份牌的代表画家和技法是什么？",
     "传统文化", "技术直答",
     ["杭稚英", "金梅生", "擦笔水彩", "技法"], "通识拓展545·新卡"),
    ("QB-1869", "香烟画片（烟画）是什么？有什么玩法？",
     "传统文化", "技术直答",
     ["烟画", "香烟画片", "集换", "题材"], "通识拓展545·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展545"],
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
    bank["version"] = "v8.10"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
