# -*- coding: utf-8 -*-
"""seed_common_447_cards.py · 通识拓展批次447知识卡+题库（幂等）

447：3 张新卡·健康饮食作息三连（牛奶 kp_card_milk / 豆浆与豆制品
    kp_card_soybean / 午睡的科学 kp_card_powernap）。
预检已过（QB-1579~1581 可用，三主题题库 0 覆盖、卡库无同名卡；
酸奶 QB-327、蜂蜜 QB-1119 已有题排除）。
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
             "XMind", "HDR", "Robotaxi", "NASA"}


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
    ("kp_card_milk",
     "牛奶",
     "饮食常识知识点内容（人话接口）", "生活常识",
     "牛奶——最常见的营养饮品：①**营养**——优质蛋白（酪蛋白+乳清蛋白）"
     "+钙（易吸收，是膳食钙的最佳来源之一）+维生素D/A/B2；②**什么时候"
     "喝**——时间不苛求，随餐或睡前均可（睡前喝≠直接助眠，主要是仪式"
     "感与避免空腹）；③**乳糖不耐受**——喝奶腹胀腹泻是体内乳糖酶少："
     "可选零乳糖奶/酸奶/奶酪，或少量多次+不空腹喝；④**选择**——纯牛"
     "奶配料表只有「生牛乳」；巴氏鲜奶（冷藏、保质期短）与常温奶营养"
     "差别不大；⑤**误区**——牛奶不是喝越多越好，每日 300-500ml 即可"
     "（膳食指南推荐）。",
     ["牛奶的营养", "牛奶什么时候喝最好", "乳糖不耐受怎么办",
      "巴氏奶和常温奶区别", "每天喝多少牛奶", "牛奶误区"],
     ["问酸奶", "问补钙"],
     "atomic", "",
     "牛奶=优质蛋白酪蛋白乳清+钙易吸收膳食钙最佳来源+随餐睡前均可+乳"
     "糖不耐受选零乳糖奶酸奶少量多次不空腹+纯牛奶配料只有生牛乳巴氏"
     "常温营养差别不大+每日300到500ml不是越多越好。"),
    ("kp_card_soybean",
     "豆浆与豆制品",
     "饮食常识知识点内容（人话接口）", "生活常识",
     "豆浆与豆制品——植物蛋白的代表：①**豆浆的营养**——大豆蛋白（唯"
     "一媲美动物蛋白的植物蛋白）+大豆异黄酮+不饱和脂肪酸，不含胆固醇；"
     "②**必须煮熟**——生豆浆含皂苷和胰蛋白酶抑制剂，没煮透会恶心呕"
     "吐（「假沸」现象：80℃ 左右泡沫上涌并非真沸腾，要继续加热 5 分钟"
     "以上）；③**豆制品家族**——豆腐（北豆腐硬/南豆腐嫩）、豆浆、腐"
     "竹、豆干——钙含量：豆干>北豆腐>南豆腐>豆浆（豆浆钙其实不多）；"
     "④**谣言澄清**——正常喝豆浆不会导致性早熟（异黄酮活性远弱于人"
     "体雌激素）；痛风缓解期可适量喝（嘌呤含量中等偏低）；⑤**搭配**"
     "——豆类+谷物蛋白互补（豆浆+馒头/杂粮饭）。",
     ["豆浆和牛奶哪个好", "豆浆必须煮熟吗", "假沸是什么",
      "豆腐有哪些种类", "喝豆浆会性早熟吗", "豆制品营养"],
     ["问牛奶", "问蛋白质"],
     "atomic", "",
     "豆浆豆制品=大豆蛋白媲美动物蛋白异黄酮不含胆固醇+生豆浆皂苷胰蛋"
     "白酶抑制剂必须煮透假沸80度泡沫非真沸继续加热5分钟+豆腐豆浆腐竹"
     "豆干钙含量豆干最高+正常喝不导致性早熟异黄酮活性弱+豆类谷物蛋白"
     "互补。"),
    ("kp_card_powernap",
     "午睡的科学",
     "健康习惯知识点内容（人话接口）", "健康与身体",
     "午睡——科学的「中场休息」：①**时长是关键**——20-30 分钟最佳："
     "只到浅睡阶段，醒来清爽；超过 1 小时进入深睡眠，醒来反而昏沉（睡"
     "眠惰性）；②**时间点**——下午 1-3 点最符合人体节律（此时警觉性"
     "自然低谷）；太晚午睡会影响晚上入睡；③**NASA 研究**——飞行员"
     "小睡 26 分钟，警觉性提升约 54%；「咖啡因小睡」：喝完咖啡立刻"
     "小睡 20 分钟，醒来时咖啡因起效+睡眠恢复双叠加；④**姿势**——"
     "别趴在桌上午睡（压迫眼球与手臂麻木），用折叠躺椅或颈枕靠背；"
     "⑤**不是人人必须**——夜间睡眠充足且白天精神好的人，不午睡也"
     "完全正常。",
     ["午睡多久最好", "午睡越睡越困为什么", "咖啡因小睡",
      "趴着午睡的危害", "午睡时间点", "不午睡正常吗"],
     ["问睡眠质量", "问失眠"],
     "atomic", "",
     "午睡=20到30分钟最佳超过1小时深睡眠醒后昏沉睡眠惰性+下午1到3点"
     "符合节律太晚影响夜间入睡+NASA飞行员小睡26分钟警觉性升54%咖啡因"
     "小睡喝完立刻睡20分钟双叠加+别趴桌压眼用躺椅颈枕+夜间睡足白天精"
     "神好不午睡也正常。"),
]

QUESTIONS = [
    ("QB-1579", "牛奶有什么营养？乳糖不耐受的人怎么喝奶？",
     "生活常识", "技术直答",
     ["牛奶", "营养", "乳糖不耐受", "补钙"], "通识拓展447"),
    ("QB-1580", "豆浆和牛奶的营养有什么区别？为什么豆浆必须煮熟？",
     "生活常识", "技术直答",
     ["豆浆", "豆制品", "煮熟", "营养"], "通识拓展447"),
    ("QB-1581", "午睡多久最合适？为什么午睡越睡越困？",
     "健康与身体", "技术直答",
     ["午睡", "时长", "睡眠惰性", "休息"], "通识拓展447"),
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
                               "level:L2", "status:verified", "batch:通识拓展447"],
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
    bank["version"] = "v7.18"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
