# -*- coding: utf-8 -*-
"""seed_common_548_cards.py · 通识拓展批次548知识卡+题库（幂等）

548：2 张新卡·灯彩糖艺域（灯彩 kp_card_dengcai /
    糖画 kp_card_tanghua——id 与语义等价卡名双重确认双零；
    紫砂壶 kp_card_zisha、折纸 kp_card_origami 已有卡查重跳过）。
预检已过（QB-1876~1878 可用）。
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
    ("kp_card_dengcai",
     "灯彩",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "灯彩——把光做成的艺术：①**宫灯**——北京宫灯六角八棱、紫檀红木"
     "为架、绢纱作面绘山水花鸟，本是宫廷照明礼器，庄重华贵；②**走马灯"
     "**——灯内烛火烧热空气推动叶轮，人马剪影循环转动，是古代的「热"
     "力学玩具」，南宋《武林旧事》已有记载，成语「走马灯似的」即由此"
     "来；③**灯会**——元宵赏灯自汉代燃灯祭太一之俗相沿，南京秦淮灯会"
     "、四川自贡灯会、泉州花灯各擅胜场，秦淮灯会、自贡灯会均列入国家级"
     "非遗；④**自贡灯会**——以体型巨大、声光电结合著称，「天下第一灯"
     "」；⑤**泉州花灯**——无骨灯与刻纸料丝灯精巧绝伦。",
     ["宫灯", "走马灯", "灯彩", "秦淮灯会", "自贡灯会",
      "泉州花灯"],
     ["问元宵节", "问风筝民俗"],
     "atomic", "",
     "灯彩=宫灯六角八棱紫檀架绢纱面宫廷礼器+走马灯热气推叶轮人马循环古"
     "代热力学玩具武林旧事已载成语走马灯似的+元宵赏灯汉燃灯祭太一相沿"
     "+秦淮灯会自贡灯会国家级非遗自贡声光电天下第一灯+泉州无骨灯刻纸料"
     "丝灯精巧。"),
    ("kp_card_tanghua",
     "糖画",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "糖画——一勺糖稀画出的甜蜜江湖：①**是什么**——民间艺人以铜勺舀"
     "熬化的糖稀，在光石板上一气呵成画出龙凤花鸟，冷凝后粘上竹签即成"
     "，又称「糖关刀」；②**讲究**——糖温火候全凭手感：太热则淌、太凉"
     "则凝，手腕走线不能停顿，「一笔画」功夫；③**场景**——庙会、学校"
     "门口的糖画摊是几代人的童年，转糖画转盘「龙」最难得最受欢迎；④**"
     "源流**——唐代已有糖戏雏形，盛于四川，成都糖画 2008 年列入国家级"
     "非物质文化遗产；⑤**技艺同门**——与吹糖人、捏面人同为民艺「甜蜜"
     "三绝」。",
     ["糖画", "糖关刀", "糖稀", "成都糖画",
      "吹糖人", "庙会糖画"],
     ["问泥人与面塑", "问庙会与灯谜"],
     "atomic", "",
     "糖画=铜勺舀糖稀石板一气呵成龙凤花鸟冷凝粘竹签又称糖关刀+糖温手"
     "感太热淌太凉凝一笔画不停顿+庙会校门口转盘龙最难得童年+唐代糖戏雏"
     "形盛于四川成都糖画2008国家级非遗+吹糖人捏面人甜蜜三绝。"),
]

QUESTIONS = [
    ("QB-1876", "走马灯为什么会转？「走马灯似的」这个比喻怎么来的？",
     "传统文化", "技术直答",
     ["走马灯", "热气", "叶轮", "比喻"], "通识拓展548·新卡"),
    ("QB-1877", "中国有哪些著名的灯会？宫灯有什么特点？",
     "传统文化", "技术直答",
     ["灯会", "秦淮", "自贡", "宫灯"], "通识拓展548·新卡"),
    ("QB-1878", "糖画是怎么做出来的？为什么说它是「一笔画」？",
     "传统文化", "技术直答",
     ["糖画", "糖稀", "一笔画", "成都"], "通识拓展548·新卡"),
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
                               "level:L2", "status:verified", "batch:通识拓展548"],
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
    bank["version"] = "v8.13"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
