# -*- coding: utf-8 -*-
"""seed_common_505_cards.py · 通识拓展批次505知识卡+题库（幂等）

505：2 张新卡 + 1 张存量卡补题·名著历法域（v7.70 整数版）
    （傲慢与偏见 kp_card_prideprejudice / 二十四节气 kp_card_solarterms
    新卡——按卡名精确确认双零；《简·爱》kp_card_janeeyre 存量补题，
    女主人公角度与 QB-1678 作者题不重复）。
预检已过（QB-1747~1749 可用）。
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
    ("kp_card_prideprejudice",
     "傲慢与偏见",
     "世界文学知识点内容（人话接口）", "艺术学堂",
     "《傲慢与偏见》——简·奥斯汀的代表作：①**作者**——简·奥斯汀"
     "（1775-1817），英国女作家，六部完整长篇还包括《理智与情感》《爱"
     "玛》等，被誉为描写日常生活的圣手；②**成书**——1813 年出版，最初"
     "书稿题为《第一印象》；③**主线**——乡绅家二女儿伊丽莎白与富家子"
     "弟达西先生：达西的「傲慢」与伊丽莎白的「偏见」先入为主互相看不顺"
     "眼，经历误会与考验后相知相爱——「傲慢让别人无法爱我，偏见让我无"
     "法爱别人」；④**婚恋观**——对比三条婚姻路：为财产结婚（夏洛特嫁"
     "柯林斯）、为私欲私奔（莉迪亚）、为爱与尊重结合（伊丽莎白与达西"
     "），主张婚姻须以感情与人格平等为基础；⑤**背景**——班纳特家五女"
     "儿、家产只能传侄子的限嗣继承困境，折射当时英国乡绅社会。",
     ["傲慢与偏见是谁写的", "伊丽莎白和达西", "简·奥斯汀",
      "第一印象", "傲慢与偏见讲什么", "婚恋观"],
     ["问简爱", "问呼啸山庄"],
     "atomic", "",
     "傲慢与偏见=简·奥斯汀1813年代表作原稿题第一印象理智与情感爱玛作"
     "者+伊丽莎白与达西傲慢偏见互相看不顺眼后相知相爱+三条婚姻路为财"
     "产为私欲为爱与尊重+婚姻以感情人格平等为基础+班纳特五姐妹限嗣继"
     "承英国乡绅社会。"),
    ("kp_card_solarterms",
     "二十四节气",
     "传统历法知识点内容（人话接口）", "传统文化",
     "二十四节气——中国人观察太阳的历法智慧：①**原理**——地球绕太阳"
     "公转，太阳黄经每转过 15° 定为一个节气，一年恰好 24 个；②**四组"
     "功能**——「四立」（立春立夏立秋立冬）标志季节开始；「二分二至"
     "」（春分秋分昼夜均分、夏至冬至日照极值）是天文基准；小暑大暑小"
     "寒大寒反映温度，雨水谷雨小雪大雪反映降水，白露寒露霜降反映水汽"
     "凝结，惊蛰清明小满芒种反映物候农事；③**口诀**——「春雨惊春清谷"
     "天，夏满芒夏暑相连，秋处露秋寒霜降，冬雪雪冬小大寒」；④**地位"
     "**——起源于黄河流域农耕文明，汉代写入《太初历》沿用至今，2016"
     " 年列入联合国人类非物质文化遗产，被誉为「中国第五大发明」；⑤**"
     "应用**——农事（芒种忙种）、养生（冬至进补数九）都依它安排。",
     ["二十四节气怎么划分", "二十四节气有哪些", "节气的口诀",
      "立春立夏立秋立冬", "节气是按什么定的", "非物质文化遗产节气"],
     ["问阴历阳历", "问清明节"],
     "atomic", "",
     "二十四节气=太阳黄经每15度一个一年24个+四立季节开始二分二至天文"
     "基准小大暑小大寒温度雨水谷雨小雪大雪降水白露寒露霜降凝结惊蛰清"
     "明小满芒种物候农事+口诀春雨惊春清谷天+黄河流域汉代太初历2016年"
     "人类非遗中国第五大发明+农事养生依它安排。"),
]

QUESTIONS = [
    ("QB-1747", "《傲慢与偏见》的作者是谁？伊丽莎白和达西的主线是什么？",
     "文学常识", "技术直答",
     ["傲慢与偏见", "简·奥斯汀", "伊丽莎白", "达西"], "通识拓展505·新卡"),
    ("QB-1748", "二十四节气是按什么划分的？有哪些节气反映降水？",
     "传统文化", "技术直答",
     ["二十四节气", "太阳黄经", "雨水", "谷雨"], "通识拓展505·新卡"),
    ("QB-1749", "《简·爱》的女主人公有什么品质？为什么打动读者？",
     "文学常识", "技术直答",
     ["简·爱", "自尊", "独立", "平等"], "通识拓展505·存量补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展505"],
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
    bank["version"] = "v7.70"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
