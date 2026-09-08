# -*- coding: utf-8 -*-
"""seed_common_547_cards.py · 通识拓展批次547知识卡+题库（幂等）

547：1 张新卡 + 1 张存量卡补题·绢羽民俗域
    （绒花与绢人 kp_card_ronghua 新卡——id 与语义等价卡名双重确认双零；
    风筝民俗补题挂 kp_card_kite——与 QB-1034 物理原理题不重复）。
预检已过（QB-1873~1875 可用）。
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
    ("kp_card_ronghua",
     "绒花与绢人",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "绒花与绢人——蚕丝捏出的荣华与人烟：①**绒花**——南京绒花以蚕丝"
     "绒制假花头饰，「绒花」谐音「荣华」，明清为宫廷贡品（宫女头上的"
     "「宫花」即它）；二次元古装剧带火后再度翻红，非遗传承人赵树宪手工"
     "复刻剧中头饰；②**工艺**——蚕丝染色后以铜丝勾条、搓绒成型，「一"
     "朵花百道工序」；③**绢人**——北京绢人以丝绢纱绸塑造人物，脸手用"
     "蚕丝，戏曲人物与侍女最为传神，是「立体的工笔画」；④**共同点**——"
     "皆以蚕丝为魂，娇贵怕潮怕晒，全凭手上功夫。",
     ["绒花", "绢人", "南京绒花", "赵树宪",
      "荣华谐音", "北京绢人"],
     ["问剪纸流派", "问蚕丝"],
     "atomic", "",
     "绒花绢人=南京绒花蚕丝绒假花谐音荣华明清宫廷贡品宫花+古装剧翻红"
     "赵树宪复刻头饰+蚕丝染色铜丝勾条搓绒一朵花百道工序+北京绢人丝绢纱"
     "绸塑人物立体的工笔画戏曲侍女传神+蚕丝为魂娇贵怕潮手上功夫。"),
]

QUESTIONS = [
    ("QB-1873", "南京绒花为什么被称为「荣华」？它曾是宫廷贡品吗？",
     "传统文化", "技术直答",
     ["绒花", "荣华", "南京", "宫廷"], "通识拓展547·新卡"),
    ("QB-1874", "北京绢人是什么工艺？为什么叫「立体的工笔画」？",
     "传统文化", "技术直答",
     ["绢人", "丝绢", "人物", "工笔"], "通识拓展547·新卡"),
    ("QB-1875", "潍坊为什么被称为「世界风筝都」？北京沙燕风筝有什么讲究？",
     "传统文化", "技术直答",
     ["潍坊", "风筝都", "沙燕", "国际风筝会"], "通识拓展547·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展547"],
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
    bank["version"] = "v8.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
