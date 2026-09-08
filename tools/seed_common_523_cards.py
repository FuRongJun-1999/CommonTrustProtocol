# -*- coding: utf-8 -*-
"""seed_common_523_cards.py · 通识拓展批次523知识卡+题库（幂等）

523：1 张新卡·杂技域（杂技与幻术 kp_card_zaji——id 与语义等价卡名
    双重确认双零；脸谱 QB-1242/1517、京剧行当均已覆盖跳过；
    QB-1496「魔术贴」为仿生学题，幻术表演角度仍空缺故可立）。
预检已过（QB-1801~1803 可用）。
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
    ("kp_card_zaji",
     "杂技与幻术",
     "传统艺术知识点内容（人话接口）", "艺术学堂",
     "杂技与幻术——最古老的身体艺术：①**古称**——秦汉称「角抵」「百"
     "戏」：摔跤式竞技加杂技幻术歌舞大汇演，汉代画像石上常见倒立叠案"
     "，「鱼龙曼延」（鱼龙变装的幻术大戏）是汉代百戏招牌；②**经典项"
     "目**——顶碗、蹬技（脚蹬伞缸）、柔术（咬花下腰）、走钢丝、抖空"
     "竹、车技；口技更有名篇——「京中有善口技者」一场火灾救全场；"
     "③**吴桥**——河北吴桥是「杂技之乡」，民谣「上至九十九，下至刚会"
     "走，吴桥耍玩艺儿，人人有一手」，吴桥国际杂技节与摩纳哥蒙特卡洛"
     "马戏节、法国巴黎未来杂技节并称世界三大杂技赛场；④**幻术**——"
     "汉代已有吐火、自缚自解等西域传来戏法，是魔术的古代前身；⑤**地"
     "位**——杂技（吴桥杂技等）2006 年列入国家级非物质文化遗产。",
     ["杂技的由来", "百戏", "角抵", "鱼龙曼延", "吴桥杂技",
      "口技"],
     ["问木偶戏", "问京剧"],
     "atomic", "",
     "杂技幻术=秦汉角抵百戏大汇演鱼龙曼延幻术招牌汉代画像石倒立叠案+"
     "顶碗蹬技柔术走钢丝口技京中善口技者+河北吴桥杂技之乡上至九十九下"
     "至刚会走国际杂技节三大赛场+幻术吐火自缚自解西域传入魔术前身+"
     "2006年国家级非遗。"),
]

QUESTIONS = [
    ("QB-1801", "杂技在古代叫什么？汉代「百戏」包括什么？",
     "传统文化", "技术直答",
     ["杂技", "百戏", "角抵", "汉代"], "通识拓展523·新卡"),
    ("QB-1802", "河北吴桥为什么被称为杂技之乡？有什么国际影响？",
     "传统文化", "技术直答",
     ["吴桥", "杂技之乡", "国际杂技节", "非遗"], "通识拓展523·新卡"),
    ("QB-1803", "古代的「幻术」是什么？「鱼龙曼延」讲的是什么节目？",
     "传统文化", "技术直答",
     ["幻术", "鱼龙曼延", "百戏", "魔术"], "通识拓展523·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展523"],
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
    bank["version"] = "v7.88"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
