# -*- coding: utf-8 -*-
"""seed_common_397_cards.py · 通识拓展批次397知识卡+题库（幂等）

397：3 张新卡（电影 kp_card_cinema / 动画片 kp_card_animation /
    纪录片 kp_card_documentary）+ 3 题（QB-1429~1431）。
KCCS 四要素+题干原句触发词。预检已过（QB-1429~1431 可用，
影视三主题题库卡库双零）。
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
             "MTBF", "SQA"}


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
    ("kp_card_cinema",
     "电影",
     "影视常识知识点内容（人话接口）", "文化娱乐",
     "电影——「第七艺术」：①**诞生**——1895 年法国卢米埃尔兄弟在巴黎"
     "首次公映售票电影，标志电影时代开始；②**技术演进**——默片时代"
     "（卓别林靠肢体喜剧征服观众）→1927 年有声电影出现→1935 年彩色"
     "电影普及→数字摄影与巨幕格式；③**成像原理**——每秒 24 帧的静止"
     "画面连续播放，利用人眼「视觉暂留」（似动现象）产生连续运动感；"
     "④**重要奖项**——美国奥斯卡金像奖、法国戛纳金棕榈奖、威尼斯金狮"
     "奖、柏林金熊奖，中国有金鸡奖与百花奖；⑤**行业分工**——导演/"
     "编剧/摄影/剪辑/特效各司其职，「剪辑」被称为电影的第二次创作。",
     ["电影是谁发明的", "电影为什么每秒24帧", "默片时代",
      "奥斯卡金像奖", "戛纳金棕榈", "电影发展史"],
     ["问动画", "问摄影"],
     "atomic", "",
     "电影=1895卢米埃尔兄弟巴黎首映+默片卓别林到1927有声1935彩色再到"
     "数字巨幕+每秒24帧视觉暂留似动现象+奥斯卡戛纳金棕榈威尼斯金狮柏"
     "林金熊金鸡百花+剪辑是第二次创作。"),
    ("kp_card_animation",
     "动画片",
     "影视常识知识点内容（人话接口）", "文化娱乐",
     "动画片——逐帧创造运动的影视形式：①**制作类型**——二维手绘"
     "（每张画一幅）、定格动画（木偶/黏土/剪纸实体逐格摆拍，如经典"
     "木偶片）、三维动画（电脑建模渲染）；②**中国学派**——上海美术"
     "电影制片厂创造水墨动画（《小蝌蚪找妈妈》世界首创水墨技法）、"
     "《大闹天宫》《哪吒闹海》享誉世界；③**国际格局**——美国迪士尼"
     "开创长篇动画、皮克斯开创三维长片；日本宫崎骏与吉卜力工作室以"
     "手绘细腻叙事著称（《千与千寻》获奥斯卡）；④**一秒的代价**——"
     "传统手绘动画一秒要 24 张画（一拍一），长片动辄十几万张原画；⑤**"
     "本质**——动画不是「给小孩看的」，是用绘画自由表达想象力的艺术"
     "形式。",
     ["动画片是怎么做出来的", "定格动画是什么", "水墨动画",
      "大闹天宫", "宫崎骏", "三维动画和二维动画"],
     ["问电影史", "问特效"],
     "atomic", "",
     "动画=二维手绘定格摆拍三维建模三大类型+上美影水墨动画小蝌蚪找妈"
     "妈世界首创大闹天宫哪吒闹海+迪士尼皮克斯宫崎骏吉卜力千与千寻+手"
     "绘一秒24张长片十几万张+自由表达想象力的艺术。"),
    ("kp_card_documentary",
     "纪录片",
     "影视常识知识点内容（人话接口）", "文化娱乐",
     "纪录片——以真实为生命的非虚构影像：①**核心原则**——不虚构情节"
     "、不摆拍造假，用真实素材呈现世界（「真实是纪录片的生命线」）；②"
     "**类型**——自然类（BBC《地球脉动》以航拍与微距拍到前所未见的"
     "自然奇观）、历史人文类、科技类、美食社会类；③**中国现象级作品**"
     "——《舌尖上的中国》让美食纪录片成为全民话题，《我在故宫修文物》"
     "让文物修复师走红；④**与电影区别**——剧情片演绎虚构故事，纪录片"
     "捕捉和解释真实世界（但同样需要视角、剪辑与叙事结构）；⑤**价值**"
     "——存档时代记忆、科普知识、促进跨文化理解。",
     ["纪录片是什么", "纪录片和电影区别", "地球脉动",
      "舌尖上的中国", "我在故宫修文物", "纪录片怎么拍"],
     ["问新闻", "问自然摄影"],
     "atomic", "",
     "纪录片=非虚构真实是生命线不摆拍造假+自然BBC地球脉动历史人文科技"
     "美食类型+舌尖上的中国我在故宫修文物现象级+与剧情片区别在捕捉真"
     "实仍需视角剪辑叙事+存档时代记忆科普跨文化理解。"),
]

QUESTIONS = [
    ("QB-1429", "电影是什么时候诞生的？电影为什么每秒是24帧？",
     "文化娱乐", "技术直答",
     ["电影", "卢米埃尔", "帧", "视觉暂留"], "通识拓展397"),
    ("QB-1430", "动画片有哪些制作类型？中国水墨动画有什么地位？",
     "文化娱乐", "技术直答",
     ["动画", "水墨", "定格", "三维"], "通识拓展397"),
    ("QB-1431", "纪录片和电影有什么区别？有哪些经典纪录片？",
     "文化娱乐", "技术直答",
     ["纪录片", "真实", "区别", "经典"], "通识拓展397"),
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
                               "level:L2", "status:verified", "batch:通识拓展397"],
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
    bank["version"] = "v6.67"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
