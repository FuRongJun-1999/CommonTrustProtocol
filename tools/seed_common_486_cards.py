# -*- coding: utf-8 -*-
"""seed_common_486_cards.py · 通识拓展批次486知识卡+题库（幂等）

486：3 张新卡·艺术名家三连（肖邦 kp_card_chopin /
    柴可夫斯基 kp_card_tchaikovsky / 徐悲鸿与齐白石
    kp_card_xuqibai）。预检已过（QB-1693~1695 可用，
    三主题题库卡库双零）。
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
    ("kp_card_chopin",
     "肖邦",
     "音乐名家知识点内容（人话接口）", "世界文化",
     "肖邦（1810-1849，波兰）——「钢琴诗人」：①**生平**——波兰作曲家"
     "钢琴家，20 岁离开波兰后终生未归，逝后心脏按其遗愿运回华沙；②**"
     "创作**——几乎所有作品都为钢琴而作：夜曲（宁静抒情）、玛祖卡"
     "（波兰民间舞曲）、波洛涅兹（庄严的波兰舞曲，饱含爱国深情）、"
     "练习曲；③**风格**——诗意旋律与民族旋律融合——把对祖国波兰的"
     "思念写进每个音符（「把我的心脏带回祖国」）；④**地位**——浪漫"
     "主义音乐代表人物，钢琴演奏与创作的双重标杆。",
     ["肖邦是哪国人", "钢琴诗人是谁", "肖邦的代表作",
      "夜曲", "玛祖卡波洛涅兹", "肖邦的故事"],
     ["问李斯特", "问舒曼"],
     "atomic", "",
     "肖邦=波兰1810到1849钢琴诗人+20岁离波终生未归心脏遗愿运回华沙+"
     "作品几乎全为钢琴夜曲玛祖卡波洛涅兹练习曲+诗意旋律融合波兰民族"
     "元素饱含爱国深情+浪漫主义音乐代表钢琴创作演奏双重标杆。"),
    ("kp_card_tchaikovsky",
     "柴可夫斯基",
     "音乐名家知识点内容（人话接口）", "世界文化",
     "柴可夫斯基（1840-1893，俄国）——俄罗斯浪漫主义音乐大师：①**"
     "代表作**——芭蕾舞剧《天鹅湖》《胡桃夹子》《睡美人》（芭蕾音乐"
     "三大经典）、《第一钢琴协奏曲》、歌剧《叶甫盖尼·奥涅金》；②**"
     "风格**——旋律优美深情、情感浓烈真挚，把俄罗斯民族音乐与西方古"
     "典技法完美融合；③**《天鹅湖》**——四小天鹅舞曲轻盈灵动家喻户晓"
     "；④**地位**——俄罗斯音乐的旗帜人物，柴可夫斯基国际音乐比赛是"
     "世界顶级音乐赛事。",
     ["柴可夫斯基是哪国人", "天鹅湖作者是谁",
      "胡桃夹子", "柴可夫斯基代表作", "俄罗斯音乐家",
      "第一钢琴协奏曲"],
     ["问肖邦", "问芭蕾舞剧"],
     "atomic", "",
     "柴可夫斯基=俄国1840到1893浪漫主义音乐大师+天鹅湖胡桃夹子睡美人"
     "芭蕾三大经典第一钢琴协奏曲叶甫盖尼奥涅金+旋律优美深情俄民族音乐"
     "融合西方技法+四小天鹅舞曲家喻户晓+俄罗斯音乐旗帜柴赛顶级赛事。"),
    ("kp_card_xuqibai",
     "徐悲鸿与齐白石",
     "艺术名家知识点内容（人话接口）", "传统文化",
     "中国近现代画坛双璧：①**徐悲鸿**（1895-1953）——以画马著称：奔"
     "马笔下的骏马雄健奔放；融合西方写实技法与中国水墨（留学法国），"
     "代表作《奔马图》《愚公移山》；主张「古法之佳者守之，西方绘画可"
     "采入者融之」；还是杰出美术教育家（中央美院首任院长）；②**齐白"
     "石**（1864-1957）——木匠出身的大画家：画虾最负盛名（水墨虾晶莹"
     "剔透），主张「妙在似与不似之间」；花鸟鱼虫瓜果菜蔬皆入画，质朴"
     "天真；衰年变法（「红花墨叶」风格）成就艺术巅峰；③**共同点**——"
     "根植传统又勇于创新，作品雅俗共赏。",
     ["徐悲鸿画马", "齐白石画虾", "愚公移山徐悲鸿",
      "衰年变法", "妙在似与不似之间", "中国近现代画家"],
     ["问张大千", "问中国画"],
     "atomic", "",
     "徐悲鸿齐白石=徐悲鸿画马奔马图愚公移山融西写实于水墨中央美院首任"
     "院长+齐白石木匠出身画虾最负盛名妙在似与不似之间衰年变法红花墨叶+"
     "根植传统勇于创新雅俗共赏+近现代画坛双璧。"),
]

QUESTIONS = [
    ("QB-1693", "「钢琴诗人」肖邦是哪国人？他的代表作品有哪些？",
     "世界文化", "技术直答",
     ["肖邦", "钢琴诗人", "夜曲", "波兰"], "通识拓展486"),
    ("QB-1694", "《天鹅湖》的作者是谁？柴可夫斯基有哪些代表作？",
     "世界文化", "技术直答",
     ["柴可夫斯基", "天鹅湖", "胡桃夹子", "俄国"], "通识拓展486"),
    ("QB-1695", "徐悲鸿擅长画什么？齐白石画虾有什么艺术主张？",
     "传统文化", "技术直答",
     ["徐悲鸿", "齐白石", "奔马", "画虾"], "通识拓展486"),
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
                               "level:L2", "status:verified", "batch:通识拓展486"],
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
    bank["version"] = "v7.52"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
