# -*- coding: utf-8 -*-
"""seed_common_541_cards.py · 通识拓展批次541知识卡+题库（幂等）

541：2 张新卡·收藏集藏域（集邮 kp_card_youpiao /
    钱币收藏 kp_card_gubbi——id 与语义等价卡名双重确认双零）。
预检已过（QB-1855~1857 可用）。
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
    ("kp_card_youpiao",
     "集邮",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "集邮——方寸之间的世界史：①**世界第一枚邮票**——英国「黑便士"
     "」（1840 年），罗兰·希尔改革邮政有功，被誉为「邮票之父」；②**"
     "中国第一套**——1878 年清朝海关邮政发行的「大龙邮票」，蟠龙图案"
     "；③**传奇错票**——1968 年《全国山河一片红》因地图绘制错误紧急"
     "回收，存世极少成为顶级名票；④**集邮要素**——品相（齿孔完整、背"
     "胶好、无折痕）、实寄封（真实寄递过的信封）、首日封（发行首日盖戳"
     "）都是研究对象；⑤**意义**——一枚邮票就是一扇窗：政治、艺术、科"
     "技、风物尽在方寸之间。",
     ["集邮", "黑便士", "大龙邮票", "全国山河一片红",
      "首日封", "罗兰希尔"],
     ["问古玩行话", "问钱币收藏"],
     "atomic", "",
     "集邮=黑便士1840英国罗兰希尔邮票之父+大龙邮票1878清朝海关邮政中"
     "国第一套蟠龙图案+全国山河一片红1968地图错误紧急回收存世极少顶级"
     "名票+品相齿孔背胶实寄封首日封+一枚邮票一扇窗方寸见世界。"),
    ("kp_card_gubbi",
     "钱币收藏",
     "收藏集藏知识点内容（人话接口）", "传统文化",
     "钱币收藏——泉友的方孔乾坤：①**古称**——钱古称「泉」，取如泉水"
     "流通之意，钱币藏家互称「泉友」；②**古钱谱系**——从贝币到方孔圆"
     "钱（详见古货币卡），历代泉谱（钱谱）浩如烟海；③**机制币**——晚"
     "清引进造币机器铸银元铜元：「袁大头」（民国三年袁世凯像壹圆银币"
     "）流通最广，含银约八九成；④**现代纪念币**——人民银行发行的普通"
     "纪念币与贵金属纪念币，题材纪念事件人物生肖；⑤**评级币**——送权"
     "威评级公司真伪鉴定与品相打分后封装，交易更放心；⑥**行规**——"
     "看币先看边（磨损与边齿），轻拿轻放只触边不触面。",
     ["钱币收藏", "袁大头", "古钱", "泉友",
      "纪念币", "评级币"],
     ["问古玩行话", "问古代货币"],
     "atomic", "",
     "钱币收藏=泉古称流通意泉友互称+贝币到方孔圆钱谱系泉谱浩瀚+袁大头"
     "民国三年壹圆银币流通最广含银八九成+人民银行纪念币普通贵金属两类+"
     "评级公司鉴定封装放心交易+看边轻拿只触边不触面。"),
]

QUESTIONS = [
    ("QB-1855", "世界上第一枚邮票是什么？「邮票之父」是谁？",
     "传统文化", "技术直答",
     ["黑便士", "1840", "罗兰希尔", "英国"], "通识拓展541·新卡"),
    ("QB-1856", "中国的第一套邮票是什么？大龙邮票有什么地位？",
     "传统文化", "技术直答",
     ["大龙邮票", "1878", "第一套", "蟠龙"], "通识拓展541·新卡"),
    ("QB-1857", "「袁大头」是什么钱币？为什么古称钱为「泉」？",
     "传统文化", "技术直答",
     ["袁大头", "银元", "泉", "泉友"], "通识拓展541·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展541"],
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
    bank["version"] = "v8.06"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
