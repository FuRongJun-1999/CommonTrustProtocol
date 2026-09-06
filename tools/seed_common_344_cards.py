# -*- coding: utf-8 -*-
"""seed_common_344_cards.py · 通识拓展批次344知识卡+题库（幂等）

344：健康-视疲劳的缓解/健康-水痘的识别与护理
KCCS 四要素+题干原句触发词。预检已过（QB-1271/1272+双id可用）。
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
             "Dijkstra", "Bellman", "Floyd", "logV"}


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
    ("kp_card_eyefatigue2",
     "视疲劳的缓解",
     "健康常识知识点内容（人话接口）", "生活常识",
     "眼睛累了怎么救：①**20-20-20 法则**——每用眼 20 分钟，看 20 英尺"
     "（约 6 米）外 20 秒——睫状肌放松的关键；②**环境**——屏幕亮度与环境"
     "光协调（别在黑暗里刷手机）、屏幕略低于视线、保持 50-70 厘米距离；③"
     "**干涩应对**——有意识多眨眼（专注屏幕时眨眼次数减半）、人工泪液"
     "（不含防腐剂款）、热敷促进睑板腺分泌油脂锁水；④**信号别忽视**——"
     "持续眼痛/视力骤降/视野缺损/闪光感不是「累」，立即就医（青光眼/"
     "视网膜病变信号）；⑤**根本**——睡眠充足+户外自然光（每天 2 小时"
     "户外对儿童近视预防证据最强）；⑥**护眼片骗局**——叶黄素只对特定"
     "眼底病变辅助，不能「抵消」用眼过度。",
     ["视疲劳怎么缓解", "20-20-20法则", "眼睛干涩怎么办",
      "热敷眼睛", "人工泪液", "护眼方法"],
     ["问干眼症", "问近视防控"],
     "atomic", "",
     "视疲劳=20-20-20法则睫状肌放松+屏幕亮度协调距离50-70cm+多眨眼"
     "人工泪液热敷睑板腺+持续眼痛视力骤降就医非累+户外2小时近视预防"
     "最强+叶黄素不能抵消用眼过度。"),
    ("kp_card_varicella2",
     "水痘的识别与护理",
     "健康常识知识点内容（人话接口）", "生活常识",
     "水痘常识：①**病原**——水痘-带状疱疹病毒（初次感染=水痘，病毒终身"
     "潜伏，成年后免疫力低下可复发为带状疱疹「缠腰龙」）；②**识别**——"
     "发热+分批出现的斑疹→丘疹→水疱→结痂（「四代同堂」各期皮疹同时"
     "可见，向心性分布躯干多）；③**传染性极强**——飞沫+接触疱液传播，"
     "出疹前 1-2 天到结痂都有传染性，需隔离至全部结痂；④**护理**——"
     "止痒（炉甘石洗剂）防抓破（继发感染留疤）、剪短指甲、温水浴忌热水"
     "烫洗、发热用对乙酰氨基酚（**儿童忌阿司匹林**——瑞氏综合征风险）；"
     "⑤**疫苗**——水痘疫苗已纳入儿童免疫规划（1 剂基础可加强）；⑥**"
     "成人得水痘更重**——未感染者成年后发病症状更重并发症多。",
     ["水痘是什么", "水痘怎么护理", "水痘传染期多久",
      "水痘和带状疱疹", "水痘疫苗", "水痘能用阿司匹林吗"],
     ["问麻疹风疹对比", "问疫苗接种时间表"],
     "atomic", "",
     "水痘=水痘-带状疱疹病毒初次感染(潜伏成年后带状疱疹)+发热分批皮疹"
     "四代同堂向心分布+传染性强出疹前1-2天至结痂隔离+炉甘石止痒剪指甲"
     "温水浴+儿童忌阿司匹林瑞氏综合征+疫苗已入免疫规划+成人发病更重。"),
]

QUESTIONS = [
    ("QB-1271", "视疲劳怎么缓解？20-20-20 法则是什么？", "生活常识", "技术直答",
     ["20-20-20", "眨眼", "热敷", "户外"], "通识拓展344"),
    ("QB-1272", "水痘怎么识别和护理？水痘和带状疱疹有什么关系？", "生活常识", "技术直答",
     ["水痘", "带状疱疹", "隔离", "护理"], "通识拓展344"),
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
                               "level:L2", "status:verified", "batch:通识拓展344"],
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
    bank["version"] = "v6.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
