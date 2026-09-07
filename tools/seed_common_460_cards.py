# -*- coding: utf-8 -*-
"""seed_common_460_cards.py · 通识拓展批次460知识卡+题库（幂等）

460：2 张存量卡补题（油脂 kp_card_fatsoil 反式脂肪酸角度 /
    眼皮跳的真相 kp_card_eyelid，均已在库）
    + 1 张新卡（咖啡因与健康 kp_card_caffeine，题库卡库双零）。
预检已过（QB-1615~1617 可用，三主题精确关键词 0 覆盖）。
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
    ("kp_card_caffeine",
     "咖啡因与健康",
     "健康常识知识点内容（人话接口）", "健康与身体",
     "咖啡因——最常见的天然提神物质：①**藏在哪里**——咖啡、茶、可乐、"
     "能量饮料、巧克力都含咖啡因（天然中枢神经兴奋剂）；②**怎么起效**"
     "——阻断大脑中的腺苷受体（腺苷是「困意信号」），让人暂时不觉得"
     "困；代谢半衰期约 4-6 小时——下午晚些喝咖啡会影响晚上入睡；③**"
     "适量标准**——健康成人每天 400 毫克以内（约 3-4 杯咖啡）总体安全；"
     "过量会心悸、失眠、焦虑；④**依赖与戒断**——长期大量饮用突然停用"
     "会头痛疲倦，几天即可恢复；⑤**人群提醒**——孕妇需严格限量，儿童"
     "青少年、心律不齐者应少喝或不喝。",
     ["咖啡因是什么", "咖啡因每天摄入多少", "咖啡因过量",
      "咖啡因半衰期", "晚上喝咖啡影响睡眠", "能量饮料能多喝吗"],
     ["问喝茶失眠", "问功能饮料"],
     "atomic", "",
     "咖啡因=天然中枢神经兴奋剂藏于咖啡茶可乐能量饮料巧克力+阻断腺苷"
     "受体暂时不觉困半衰期4到6小时下午晚些影响入睡+成人每天400毫克内"
     "约3到4杯安全过量心悸失眠焦虑+突然戒断头痛疲倦几天恢复+孕妇限量"
     "儿童青少年心律不齐者不喝。"),
]

QUESTIONS = [
    ("QB-1615", "油脂对人体有什么作用？反式脂肪酸的危害是什么？",
     "健康与身体", "技术直答",
     ["油脂", "反式脂肪酸", "备用能源", "危害"], "通识拓展460·存量卡补题"),
    ("QB-1616", "眼皮跳是凶兆吗？眼皮不停跳该怎么办？",
     "健康与身体", "技术直答",
     ["眼皮跳", "眼轮匝肌", "痉挛", "热敷"], "通识拓展460·存量卡补题"),
    ("QB-1617", "咖啡因藏在哪些食物里？每天摄入多少算安全？",
     "健康与身体", "技术直答",
     ["咖啡因", "咖啡", "摄入量", "提神"], "通识拓展460"),
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
                               "level:L2", "status:verified", "batch:通识拓展460"],
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
    bank["version"] = "v7.30"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
