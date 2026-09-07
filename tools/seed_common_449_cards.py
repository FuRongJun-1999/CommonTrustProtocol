# -*- coding: utf-8 -*-
"""seed_common_449_cards.py · 通识拓展批次449知识卡+题库（幂等）

449：3 张新卡·世界历史文明三连（古巴比伦与汉谟拉比 kp_card_babylon /
    罗马帝国 kp_card_rome / 启蒙运动 kp_card_enlightenment）。
预检已过（QB-1561~1563 已用、QB-1585~1587 可用，三主题
题库 0 覆盖、卡库无同名卡；拿破仑/宗教改革候选已有卡待后续批次）。
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
    ("kp_card_babylon",
     "古巴比伦与汉谟拉比法典",
     "世界历史知识点内容（人话接口）", "历史与文明",
     "古巴比伦——两河流域的文明古国：①**两河文明**——底格里斯河与幼发"
     "拉底河之间的美索不达米亚（「两河之间」），四大文明古国之一（古巴"
     "比伦/古埃及/古印度/中国）；②**汉谟拉比法典**——古巴比伦国王汉谟"
     "拉比（约公元前 18 世纪）颁布，刻在黑色玄武岩石柱上，是迄今发现的"
     "世界上第一部较完整的成文法典——「以眼还眼，以牙还牙」的同态复仇"
     "原则；③**文化贡献**——楔形文字（刻在泥板上，最古老的文字之一）"
     "、六十进制（今天 1 小时 60 分、1 圆 360 度的来源）、《吉尔伽美什》"
     "史诗；④**「空中花园」**——古代世界七大奇迹之一（传说为国王为"
     "思念山林的王妃所建，遗址尚存争议）。",
     ["古巴比伦在哪", "汉谟拉比法典是什么", "楔形文字",
      "四大文明古国", "空中花园", "六十进制的由来"],
     ["问古埃及", "问古罗马"],
     "atomic", "",
     "古巴比伦=两河流域美索不达米亚四大文明古国之一+汉谟拉比法典约前"
     "18世纪玄武岩石柱世界第一部较完整成文法典以眼还眼+楔形文字泥板最"
     "古老文字之一+六十进制来源时分秒360度+吉尔伽美什史诗+空中花园世"
     "界七大奇迹遗址存争议。"),
    ("kp_card_rome",
     "罗马帝国",
     "世界历史知识点内容（人话接口）", "历史与文明",
     "罗马帝国——古代地中海世界的霸主：①**从共和国到帝国**——罗马王"
     "政→共和国（元老院执政官）→屋大维（奥古斯都）公元前 27 年建立"
     "帝制；②**全盛**——图拉真时期版图最大（环地中海，横跨欧亚非三洲"
     "，「条条大路通罗马」的道路网）；③**文化制度遗产**——拉丁字母"
     "（今天英语法语的字母来源）、罗马法（《十二铜表法》到民法大全，"
     "近代法律体系的基石）、儒略历（公历前身）；④**分裂与灭亡**——"
     "公元 395 年分东西两罗马，西罗马 476 年灭亡（欧洲中世纪开始），"
     "东罗马（拜占庭）延续到 1453 年；⑤**建筑**——斗兽场、万神殿、"
     "引水渠，混凝土拱券技术领先。",
     ["罗马帝国什么时候建立的", "屋大维", "条条大路通罗马",
      "拉丁字母", "罗马法", "西罗马灭亡"],
     ["问古希腊", "问拜占庭"],
     "atomic", "",
     "罗马帝国=王政共和国到帝国屋大维奥古斯都前27年建帝制+图拉真版图"
     "最大环地中海条条大路通罗马+遗产拉丁字母罗马法十二铜表法儒略历+"
     "395分东西西罗马476亡中世纪开始东罗马拜占庭延至1453+斗兽场万神"
     "殿混凝土拱券。"),
    ("kp_card_enlightenment",
     "启蒙运动",
     "世界历史知识点内容（人话接口）", "历史与文明",
     "启蒙运动——17-18 世纪欧洲的思想解放运动：①**核心**——崇尚理性，"
     "反对封建专制与宗教蒙昧，倡导自由、平等、天赋人权、三权分立；②**"
     "代表人物**——伏尔泰（启蒙领袖，抨击教会专制）、孟德斯鸠（《论法"
     "的精神》三权分立学说）、卢梭（《社会契约论》人民主权）、康德"
     "（「敢于运用你自己的理智」）；③**影响**——直接推动美国独立"
     "（1776《独立宣言》）与法国大革命（1789《人权宣言》）；④**与文艺"
     "复兴的关系**——文艺复兴反神权，启蒙运动进一步反专制，从「人文"
     "」走向「理性」；⑤**传播**——启蒙思想也影响了近代中国的维新与"
     "革命思潮。",
     ["启蒙运动是什么", "启蒙运动代表人物", "三权分立是谁提出的",
      "卢梭社会契约论", "启蒙运动的影响", "理性主义"],
     ["问文艺复兴", "问法国大革命"],
     "atomic", "",
     "启蒙运动=17到18世纪欧洲思想解放崇尚理性反专制反蒙昧+伏尔泰孟德"
     "斯鸠三权分立卢梭社会契约人民主权康德敢用理智+推动美国独立法国大"
     "革命独立宣言人权宣言+文艺复兴反神权启蒙进一步反专制从人文到理性"
     "+影响近代中国维新革命思潮。"),
]

QUESTIONS = [
    ("QB-1585", "汉谟拉比法典是什么？楔形文字是哪个文明的？",
     "世界历史", "技术直答",
     ["古巴比伦", "汉谟拉比", "楔形文字", "法典"], "通识拓展449"),
    ("QB-1586", "罗马帝国是怎么建立的？西罗马帝国哪年灭亡？",
     "世界历史", "技术直答",
     ["罗马帝国", "屋大维", "西罗马", "灭亡"], "通识拓展449"),
    ("QB-1587", "启蒙运动的代表人物有哪些？三权分立是谁提出的？",
     "世界历史", "技术直答",
     ["启蒙运动", "伏尔泰", "孟德斯鸠", "三权分立"], "通识拓展449"),
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
                               "level:L2", "status:verified", "batch:通识拓展449"],
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
    bank["version"] = "v7.20"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
