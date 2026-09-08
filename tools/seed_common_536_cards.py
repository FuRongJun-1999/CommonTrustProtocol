# -*- coding: utf-8 -*-
"""seed_common_536_cards.py · 通识拓展批次536知识卡+题库（幂等）

536：2 张新卡·器物文化域（青铜器与金文 kp_card_qingtong /
    玉文化 kp_card_yuwenhua——id 与语义等价卡名双重确认无独立卡；
    后母戊鼎 kp_card_houmuwu2 已有专卡查重跳过）。
预检已过（QB-1840~1842 可用）。
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
    ("kp_card_qingtong",
     "青铜器与金文",
     "考古常识知识点内容（人话接口）", "历史与文明",
     "青铜器与金文——钟鼎里的文明密码：①**青铜**——铜锡铅合金，商周"
     "是青铜时代鼎盛期；鼎从炊煮器升格为礼器、权力的象征——「问鼎中原"
     "」（楚庄王打听周鼎轻重即被解读为觊觎王权）、「一言九鼎」皆由此；"
     "②**金文**——铸刻在青铜器上的文字，又称钟鼎文，上承甲骨文下启篆"
     "书；毛公鼎铭文近五百字，为传世青铜器铭文最长者；③**纹饰**——饕"
     "餮纹（兽面纹）狞厉威严，是神权与王权的视觉语言；④**工艺**——陶"
     "范法为主、失蜡法能铸玲珑剔透的复杂造型；⑤**名器**——后母戊鼎（"
     "世界最大青铜器之一，详见专卡）、四羊方尊、曾侯乙编钟（详见专卡"
     "）。",
     ["青铜器", "金文是什么", "问鼎中原", "毛公鼎",
      "饕餮纹", "钟鼎文"],
     ["问后母戊鼎", "问甲骨文"],
     "atomic", "",
     "青铜器金文=铜锡铅合金商周鼎盛鼎升格礼器权力象征问鼎中原一言九鼎"
     "+金文钟鼎文上承甲骨下启篆书毛公鼎近五百字最长铭文+饕餮纹兽面狞厉"
     "神权王权视觉语言+陶范法失蜡法+后母戊鼎四羊方尊曾侯乙编钟名器。"
     ),
    ("kp_card_yuwenhua",
     "玉文化",
     "传统文化知识点内容（人话接口）", "传统文化",
     "玉文化——温润千年的东方信仰：①**玉的定义**——「玉，石之美者"
     "」；儒家把玉人格化：「君子比德于玉」——温润、坚韧、纯洁皆君子之"
     "德；②**和氏璧**——楚人卞和献玉两次被诬欺君刖足，第三次剖石得"
     "宝；蔺相如持璧抵秦「完璧归赵」；相传秦以此璧琢传国玉玺，刻「受命"
     "于天，既寿永昌」，此后玺成为皇权象征（玺字从此为天子专属）；③**"
     "礼玉**——新石器时代良渚文化玉琮玉璧已是祭天礼地之器；汉代金缕玉"
     "衣以玉片金丝殓贵族；④**俗语**——「宁为玉碎，不为瓦全」「抛砖引"
     "玉」「亭亭玉立」——玉已融进汉语血液；⑤**产地**——和田玉（新疆"
     "）最负盛名。",
     ["玉文化", "君子比德于玉", "和氏璧", "完璧归赵",
      "传国玉玺", "金缕玉衣"],
     ["问青铜器", "问良渚"],
     "atomic", "",
     "玉文化=玉石之美者君子比德于玉人格化+卞和献玉刖足和氏璧蔺相如完"
     "璧归赵+相传琢传国玉玺受命于天既寿永昌玺成天子专属+良渚玉琮玉璧"
     "礼器汉代金缕玉衣+宁为玉碎不为瓦全抛砖引玉+和田玉最盛。"),
]

QUESTIONS = [
    ("QB-1840", "「金文」是什么文字？「问鼎中原」的典故出自哪里？",
     "历史常识", "技术直答",
     ["金文", "钟鼎文", "问鼎中原", "楚庄王"], "通识拓展536·新卡"),
    ("QB-1841", "「完璧归赵」讲的是谁的故事？和氏璧后来去了哪里？",
     "历史常识", "技术直答",
     ["完璧归赵", "蔺相如", "和氏璧", "传国玉玺"], "通识拓展536·新卡"),
    ("QB-1842", "为什么说「君子比德于玉」？中国人为什么爱玉？",
     "传统文化", "技术直答",
     ["玉文化", "君子", "比德", "温润"], "通识拓展536·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展536"],
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
    bank["version"] = "v8.01"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
