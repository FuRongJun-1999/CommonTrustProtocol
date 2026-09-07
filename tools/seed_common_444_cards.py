# -*- coding: utf-8 -*-
"""seed_common_444_cards.py · 通识拓展批次444知识卡+题库（幂等）

444：2 张新卡（冥想与正念 kp_card_meditation / 八段锦 kp_card_baduanjin，
    题库卡库双零——此前命中为情绪管理/太极拳卡误中）+ 1 张存量卡
    补题（春困秋乏 kp_card_springsleepy，已在库）。
养生三连。预检已过（QB-1570~1572 可用，三主题精确关键词 0 覆盖）。
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
    ("kp_card_meditation",
     "冥想与正念",
     "养生方法知识点内容（人话接口）", "健康与身体",
     "冥想——给大脑做「体操」：①**是什么**——把注意力锚定在呼吸、身体"
     "感受或当下的训练；「正念」=不加评判地觉察此刻正在发生的事；②**"
     "科学验证**——规律冥想可降低压力激素、改善睡眠与专注力，大脑"
     "前额叶（负责理性调控）的活跃度有可测量的变化；③**入门方法**——"
     "每天 5-10 分钟：闭眼坐着，专注呼吸的进出；走神了不要自责，温柔"
     "把注意力拉回来——「拉回」这个动作本身就是练习；④**应用**——"
     "缓解焦虑情绪、改善失眠、疼痛管理的辅助手段；⑤**误区**——冥想"
     "不是「什么都不想」，也不是玄学，而是一种可训练的注意力技能。",
     ["冥想是什么", "正念是什么意思", "冥想的好处",
      "冥想怎么入门", "冥想走神怎么办", "正念呼吸"],
     ["问瑜伽", "问深呼吸"],
     "atomic", "",
     "冥想正念=注意力锚定呼吸身体当下不加评判觉察+规律练习降压力激素"
     "改善睡眠专注力前额叶变化可测+每天5到10分钟闭眼专注呼吸走神温柔"
     "拉回拉回就是练习+缓解焦虑改善失眠疼痛辅助+不是什么都不想是可训"
     "练的注意力技能。"),
    ("kp_card_baduanjin",
     "八段锦",
     "传统养生知识点内容（人话接口）", "健康与身体",
     "八段锦——流传千年的健身气功：①**是什么**——八段连贯的导引动作，"
     "宋代已有文字记载，动作如锦缎般柔顺舒展得名；②**八式口诀**——"
     "两手托天理三焦、左右开弓似射雕、调理脾胃须单举、五劳七伤往后瞧、"
     "摇头摆尾去心火、两手攀足固肾腰、攒拳怒目增气力、背后七颠百病消；"
     "③**特点**——动作舒缓、无需器械、占地小，办公室与家里都能练；"
     "拉伸+呼吸配合，改善肩颈僵硬与体态；④**练习建议**——每天 1-2 遍"
     "约 15 分钟，动作到位比数量重要，循序渐进不追求幅度；⑤**地位**"
     "——与太极拳同为国家级非遗健身功法，适合各年龄段。",
     ["八段锦是什么", "八段锦口诀", "八段锦的好处",
      "八段锦怎么练", "健身气功", "八段锦适合什么人"],
     ["问太极拳", "问五禽戏"],
     "atomic", "",
     "八段锦=八段连贯导引动作宋代已有记载锦缎柔顺得名+两手托天理三焦"
     "左右开弓似射雕调理脾胃须单举五劳七伤往后瞧摇头摆尾去心火两手攀"
     "足固肾腰攒拳怒目增气力背后七颠百病消+舒缓无需器械办公室能练+每"
     "天1到2遍约15分钟动作到位比数量重要+国家级非遗健身功法。"),
]

QUESTIONS = [
    ("QB-1570", "什么是冥想？规律冥想对身体有什么好处？",
     "健康与身体", "技术直答",
     ["冥想", "正念", "呼吸", "专注"], "通识拓展444"),
    ("QB-1571", "八段锦是什么？练八段锦有什么好处？",
     "健康与身体", "技术直答",
     ["八段锦", "气功", "口诀", "健身"], "通识拓展444"),
    ("QB-1572", "「春困秋乏」是怎么回事？季节性犯困正常吗？",
     "健康与身体", "技术直答",
     ["春困", "秋乏", "犯困", "季节"], "通识拓展444·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展444"],
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
    bank["version"] = "v7.15"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
