# -*- coding: utf-8 -*-
"""seed_common_578_cards.py · 通识拓展批次578知识卡+题库（幂等）

578：1 张新卡·官服等级域（清代官服等级 kp_card_jifu——
    id 与语义等价卡名双重确认双零）。
预检已过（QB-1966~1968 可用）。
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
    ("kp_card_jifu",
     "清代官服等级",
     "制度史知识点内容（人话接口）", "历史与文明",
     "清代官服等级——穿在身上的官阶表：①**补子**——官服前胸后背的方"
     "形刺绣「补子」标品级：文官绣飞禽（一品仙鹤、二品锦鸡、三品孔雀…"
     "九品练雀），武官绣走兽（一品麒麟、二品狮子、三品豹…九品海马）；"
     "成语「衣冠禽兽」本指官员服饰，后世才转为贬义；②**顶戴**——帽顶"
     "顶珠材质分品级：一品红宝石、二品珊瑚、三品蓝宝石、四品青金石、五"
     "品水晶、六品砗磲、七至九品用金；③**花翎**——孔雀翎分单眼、双"
     "眼、三眼，三眼最尊，须皇帝特赐；蓝翎（鹖羽）赐低级侍卫；④**蟒"
     "袍**——绣四爪蟒纹，区别于皇帝五爪龙袍；⑤**意涵**——补子、顶"
     "珠、花翎三件套让官阶「一眼可辨」，是等级制度最直观的视觉表达。",
     ["补子", "顶戴花翎", "一品仙鹤", "三眼花翎",
      "蟒袍", "衣冠禽兽"],
     ["问科举制度", "问清代科场案"],
     "atomic", "",
     "官服等级=补子文飞禽武走兽一品仙鹤麒麟九品练雀海马+衣冠禽兽本指"
     "服饰后转贬+顶戴顶珠红宝石到金分九级+花翎孔雀翎单眼双眼三眼三眼最"
     "尊特赐蓝翎鹖羽+蟒袍四爪别于五爪龙袍+三件套官阶一眼可辨。"),
]

QUESTIONS = [
    ("QB-1966", "清代官服的「补子」是什么？文官武官各绣什么？",
     "历史常识", "技术直答",
     ["补子", "文官", "武官", "品级"], "通识拓展578·新卡"),
    ("QB-1967", "成语「衣冠禽兽」最初是什么意思？",
     "传统文化", "技术直答",
     ["衣冠禽兽", "补子", "官员", "贬义"], "通识拓展578·新卡"),
    ("QB-1968", "「顶戴花翎」的顶珠怎么分品级？三眼花翎有多珍贵？",
     "历史常识", "技术直答",
     ["顶戴", "花翎", "三眼", "品级"], "通识拓展578·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展578"],
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
    bank["version"] = "v8.43"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
