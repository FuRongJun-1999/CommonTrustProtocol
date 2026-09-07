# -*- coding: utf-8 -*-
"""seed_common_411_cards.py · 通识拓展批次411知识卡+题库（幂等）

411：3 张新卡·民间文化与主粮三连（舞龙舞狮 kp_card_liondance /
    庙会与灯谜 kp_card_templefair / 小麦与南北主食 kp_card_wheat）。
KCCS 四要素+题干原句触发词。预检已过（QB-1471~1473 可用，
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
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer"}


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
    ("kp_card_liondance",
     "舞龙舞狮",
     "民俗文化知识点内容（人话接口）", "传统文化",
     "舞龙舞狮——重大节庆的压轴表演：①**舞龙**——龙是中华民族的图腾，"
     "舞龙起源于祈雨祈福的仪式；数十人持竿协作，由「龙珠」引导长龙上下"
     "翻飞，讲究整体配合；②**舞狮**——分北狮（外形写实，重扑跌翻滚）"
     "与南狮（写意夸张，广东「醒狮」为代表）；南狮高潮是「采青」——"
     "狮子攀高摘取悬挂的青菜红包，寓意生生不息；③**场合与寓意**——"
     "春节、庙会、开业庆典必有，取驱邪纳吉、风调雨顺之意；④**地位**"
     "——广东醒狮等多个流派列入国家级非物质文化遗产，舞龙舞狮还走向"
     "海外华人社区，成为中华文化标识。",
     ["舞龙舞狮的由来", "南狮和北狮区别", "采青是什么意思",
      "醒狮是非遗吗", "舞龙多少人", "为什么过年舞龙舞狮"],
     ["问秧歌", "问庙会"],
     "atomic", "",
     "舞龙舞狮=龙图腾祈雨祈福龙珠引导多人协作+北狮写实南狮写意广东醒"
     "狮采青高潮寓意生生不息+春节庙会庆典驱邪纳吉+广东醒狮国家级非遗"
     "走向海外成中华文化标识。"),
    ("kp_card_templefair",
     "庙会与灯谜",
     "民俗文化知识点内容（人话接口）", "传统文化",
     "庙会——最有烟火气的传统集市：①**庙会是什么**——围绕寺庙节日或"
     "固定日期形成的集市，购物、小吃、杂耍、祭拜一体，春节庙会最盛大"
     "（地坛庙会等）；②**灯谜**——元宵节赏花灯猜灯谜：谜面挂在灯上"
     "供人竞猜，猜中有彩头；猜灯谜始于宋代，是元宵节的标志性活动"
     "（元宵节=正月十五，吃元宵/汤圆，是一年中第一个月圆之夜）；③**"
     "灯谜结构**——谜面（题目）、谜目（猜什么范围）、谜底（答案），"
     "好的灯谜讲究「回互其辞」的巧劲；④**演变**——现代庙会加入非遗"
     "展示、文创市集，成为年俗文化的集中展演场。",
     ["庙会是什么", "猜灯谜的由来", "元宵节为什么吃汤圆",
      "灯谜怎么猜", "庙会上有什么", "正月十五"],
     ["问舞龙舞狮", "问春节习俗"],
     "atomic", "",
     "庙会灯谜=寺庙节日集市购物小吃杂耍祭拜一体春节庙会最盛+元宵正月"
     "十五赏灯猜谜宋代始于谜面谜目谜底猜中有彩头+汤圆第一个月圆之夜+"
     "现代庙会加非遗文创成民俗展演场。"),
    ("kp_card_wheat",
     "小麦与南北主食",
     "农业常识知识点内容（人话接口）", "自然常识",
     "小麦——世界与中国的主粮作物：①**地位**——小麦、水稻、玉米是"
     "全球三大谷物；中国形成「南稻北麦」的主食格局——南方湿润多种"
     "水稻吃米饭，北方旱地多种小麦吃面食（馒头/面条/饺子/包子）；②**"
     "种植分类**——冬小麦（秋季播种越冬、次年夏初收获，华北主产）与"
     "春小麦（春季播种、秋季收获，东北西北为主）；③**加工**——小麦"
     "磨成面粉，面筋蛋白让面团有弹性可拉伸，是面包发酵成型的基础；"
     "④**营养**——面粉提供碳水化合物与蛋白质，全麦粉保留麸皮和胚芽"
     "（膳食纤维与B族维生素更多）。",
     ["小麦的种植", "冬小麦和春小麦", "南稻北麦",
      "小麦和水稻区别", "面粉怎么来的", "三大谷物"],
     ["问水稻", "问玉米"],
     "atomic", "",
     "小麦=全球三大谷物小麦水稻玉米+中国南稻北麦格局南方米饭北方面食"
     "+冬小麦秋播夏收华北主产春小麦春播东北西北+磨粉面筋蛋白弹性支撑"
     "面包发酵+全麦保留麸皮胚芽纤维B族更多。"),
]

QUESTIONS = [
    ("QB-1471", "舞龙舞狮有什么寓意？南狮和北狮有什么区别？",
     "传统文化", "技术直答",
     ["舞龙", "舞狮", "醒狮", "采青"], "通识拓展411"),
    ("QB-1472", "元宵节为什么要猜灯谜？庙会上都有什么？",
     "传统文化", "技术直答",
     ["庙会", "灯谜", "元宵", "花灯"], "通识拓展411"),
    ("QB-1473", "为什么中国北方多吃面食、南方多吃米饭？",
     "自然常识", "技术直答",
     ["小麦", "水稻", "南稻北麦", "主食"], "通识拓展411"),
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
                               "level:L2", "status:verified", "batch:通识拓展411"],
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
    bank["version"] = "v6.82"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
