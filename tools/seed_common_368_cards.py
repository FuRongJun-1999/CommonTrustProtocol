# -*- coding: utf-8 -*-
"""seed_common_368_cards.py · 通识拓展批次368知识卡+题库（幂等）

368：书法-王羲之/书法-颜真卿（书法新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1329/1330+双id可用）。
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
    ("kp_card_wangxizhi2",
     "王羲之：书圣",
     "书法文化知识点内容（人话接口）", "文化",
     "王羲之——书圣的传奇：①**身份**——东晋书法家（303-361 年），"
     "兼善隶/草/楷/行各体，博采众长自成一家，后世尊为「书圣」；②**"
     "《兰亭序》**——永和九年（353 年）会稽山阴兰亭雅集，微醺中写下"
     "二十八行三百二十四字（其中二十个「之」字写法各不相同），酒醒后"
     "重写数十遍皆不及原稿——「天下第一行书」；③**轶事**——「入木"
     "三分」（笔力透入木板三分深）/「东床快婿」（袒腹东床被选为郗鉴"
     "女婿）；④**家学传承**——子王献之亦是大家，父子并称「二王」"
     "（献之练字用尽十八缸水的故事）；⑤**风格**——飘若浮云，矫若"
     "惊龙；⑥**真迹不存**——唐太宗酷爱其字，传说《兰亭序》真迹随葬"
     "昭陵，今传世皆为摹本（神龙本最著名）。",
     ["王羲之是谁", "兰亭序", "天下第一行书", "入木三分",
      "东床快婿", "二王书法"],
     ["问颜真卿柳公权", "问书法入门"],
     "atomic", "",
     "王羲之=东晋书圣兼善各体+永和九年兰亭雅集微醺写兰亭序324字20个"
     "之字各不同酒醒重写不及原稿天下第一行书+入木三分东床快婿轶事+"
     "子献之二王并称十八缸水+飘若浮云矫若惊龙+唐太宗酷爱真迹传说随葬"
     "昭陵今传皆摹本。"),
    ("kp_card_yanzhenqing2",
     "颜真卿：楷书典范",
     "书法文化知识点内容（人话接口）", "文化",
     "颜真卿——忠臣书家：①**书法地位**——唐代书法家，创「颜体」楷书"
     "（端庄雄浑/气势开张/横细竖粗），与柳公权并称「颜筋柳骨」；②**"
     "代表作**——《多宝塔碑》（楷书入门范本）/《颜氏家庙碑》/《祭侄"
     "文稿》（安史之乱中祭奠侄儿，悲愤之情跃然纸上涂改满篇，被誉为"
     "「天下第二行书」）；③**人格与书格**——「字如其人」典范：刚正"
     "不阿，安史之乱中率军抗敌，晚年奉命劝降叛将李希烈被缢杀殉国；④"
     "**变法**——突破初唐瘦硬书风，变法出新（吸收篆隶笔意），影响"
     "后世千年（苏轼等皆学颜）；⑤**学书启示**——颜体强调中锋用笔/"
     "横轻竖重/结构宽博，是楷书入门主流路径；⑥** 文化地位**——与"
     "王羲之双峰并峙：王秀美流畅，颜雄浑刚健，审美两极。",
     ["颜真卿是谁", "颜体", "祭侄文稿", "颜筋柳骨",
      "多宝塔碑", "天下第二行书"],
     ["问柳公权", "问欧体赵体"],
     "atomic", "",
     "颜真卿=唐代书法家创颜体端庄雄浑横细竖粗与柳公权颜筋柳骨+多宝塔"
     "碑楷书入门范本+祭侄文稿悲愤涂改满篇天下第二行书+安史之乱率军"
     "抗敌晚年劝降叛将殉国字如其人典范+变法吸收篆隶笔意影响千年"
     "+苏轼皆学颜与王羲之双峰王秀美颜刚健。"),
]

QUESTIONS = [
    ("QB-1329", "王羲之被后人尊称为什么？《兰亭序》为什么有名？", "文化", "技术直答",
     ["书圣", "兰亭序", "天下第一行书", "王献之"], "通识拓展368"),
    ("QB-1330", "颜真卿是什么朝代的书法家？他的楷书有什么特点？", "文化", "技术直答",
     ["唐代", "颜体", "端庄", "雄浑"], "通识拓展368"),
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
                               "level:L2", "status:verified", "batch:通识拓展368"],
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
    bank["version"] = "v6.33"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"questions_added": added, "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
