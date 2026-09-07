# -*- coding: utf-8 -*-
"""seed_common_484_cards.py · 通识拓展批次484知识卡+题库（幂等）

484：3 张新卡·昆虫与鸟类三连（蜜蜂采蜜 kp_card_beehoney /
    蜻蜓 kp_card_dragonfly / 鹦鹉学舌 kp_card_parrot）。
预检已过（QB-1663~1665 已用、QB-1666~1668 已用、
QB-1669~1671 已用、QB-1678~1680 已用——空闲 QB-1663 段
实测可用；三主题题库卡库双零）。
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
    ("kp_card_beehoney",
     "蜜蜂采蜜与授粉",
     "昆虫常识知识点内容（人话接口）", "自然与生物",
     "蜜蜂——勤劳的「授粉工程师」：①**采蜜原理**——工蜂用长长的口器"
     "（喙）吸食花蜜存入蜜囊，带回蜂巢后反复吞吐加工、扇风浓缩成蜂蜜；"
     "②**授粉贡献**——蜜蜂采蜜时身上绒毛沾满花粉，在不同花朵间传递"
     "——全球约三分之一农作物依赖蜜蜂等虫媒授粉（苹果/西瓜/草莓……"
     "「没有蜜蜂，人类只能撑四年」是爱因斯坦传说名言，但授粉价值确实"
     "巨大）；③**蜂群分工**——蜂王（产卵）、雄蜂（交配）、工蜂（干活"
     "的雌性，采蜜/筑巢/保卫各司其职）；④**舞蹈语言**——圆圈舞与"
     "「8 字舞」告诉同伴蜜源方位与距离（太阳罗盘）；⑤**防御**——螫针"
     "连着毒囊，蜇人后蜜蜂自身也会死亡——防御是「生命最后一击」。",
     ["蜜蜂怎么采蜜", "蜜蜂授粉的作用", "蜂群怎么分工",
      "蜜蜂的舞蹈语言", "蜂王雄蜂工蜂", "为什么蜜蜂蜇人会死"],
     ["问蝴蝶", "问养蜂"],
     "atomic", "",
     "蜜蜂=口器吸花蜜存蜜囊回巢吞吐扇风浓缩成蜂蜜+绒毛传粉全球约三分之"
     "一农作物依赖虫媒授粉+蜂王产卵雄蜂交配工蜂采蜜筑巢保卫分工明确+"
     "圆圈舞8字舞告诉蜜源方位太阳罗盘+螫针连毒囊蜇人自身死亡防御是生"
     "命最后一击。"),
    ("kp_card_dragonfly",
     "蜻蜓",
     "昆虫常识知识点内容（人话接口）", "自然与生物",
     "蜻蜓——飞行界的「特技飞行员」：①**「蜻蜓点水」的真相**——雌"
     "蜻蜓把卵产在水中（点水=产卵），幼虫「水虿」在水里生活数月到数年"
     "捕食蚊子的幼虫孑孓；②**飞行绝技**——两对翅膀可独立振动：能悬停"
     "、倒飞、急转弯，时速可达 50 公里，是昆虫中的飞行冠军；③**复眼"
     "与捕食**——复眼由上万个小眼组成，视野接近 360 度，捕食成功率"
     "高达 90% 以上（比猎豹还高）；④**益虫**——成虫和幼虫都大量捕食"
     "蚊子苍蝇，是人类的朋友；⑤**环境指示**——蜻蜓对水质敏感，有"
     "蜻蜓飞舞的水域通常水质较好。",
     ["蜻蜓点水是什么意思", "蜻蜓为什么飞行能力强",
      "蜻蜓的复眼", "水虿是什么", "蜻蜓吃什么", "蜻蜓是益虫吗"],
     ["问蝴蝶", "问萤火虫"],
     "atomic", "",
     "蜻蜓=蜻蜓点水实为雌蜻蜓水中产卵幼虫水虿水里生活捕孑孓+两对翅独"
     "立振动悬停倒飞急转弯时速50公里飞行冠军+复眼上万小眼视野近360度"
     "捕食成功率90%以上+成虫幼虫都捕蚊蝇是益虫+水质敏感有蜻蜓水域水"
     "质较好。"),
    ("kp_card_parrot",
     "鹦鹉学舌",
     "动物常识知识点内容（人话接口）", "自然与生物",
     "鹦鹉——会「说话」的鸟：①**为什么能学人说话**——鹦鹉有发达的"
     "鸣管（发声器官）与舌头（粗厚灵活），更重要的是大脑中控制发声的"
     "「核心回路」发达；②**学舌的本质**——鹦鹉说话大多是模仿（条件"
     "反射式地把声音和场景关联），并非真正理解语义；但非洲灰鹦鹉的"
     "研究表明它们能理解数量、颜色、形状等概念（著名实验个案）；③**"
     "代表种类**——非洲灰鹦鹉（说话能力最强）、亚马逊鹦鹉、虎皮鹦鹉"
     "（小型常见宠物）；④**寿命**——大型鹦鹉寿命可达 50-80 年，是"
     "「陪伴一生的宠物」，饲养需慎重；⑤**保护**——许多野生鹦鹉是"
     "保护动物，购买饲养需合法来源。",
     ["鹦鹉为什么会说话", "鹦鹉学舌的原理", "鹦鹉能理解语言吗",
      "灰鹦鹉", "鹦鹉寿命多长", "养鹦鹉合法吗"],
     ["问八哥", "问观鸟"],
     "atomic", "",
     "鹦鹉学舌=发达鸣管粗厚灵活舌头大脑发声核心回路发达+模仿为主条件"
     "反射非真懂语义但灰鹦鹉研究显示懂数量颜色概念+非洲灰鹦鹉说话最强"
     "虎皮小型宠物+大型鹦鹉寿命50到80年陪伴一生需慎重+野生鹦鹉多保护"
     "动物购买需合法来源。"),
]

QUESTIONS = [
    ("QB-1687", "蜜蜂是怎么采蜜的？蜜蜂对人类有什么重要贡献？",
     "自然与生物", "技术直答",
     ["蜜蜂", "采蜜", "授粉", "蜂群"], "通识拓展484·存量卡补题"),
    ("QB-1688", "「蜻蜓点水」是在做什么？蜻蜓为什么是飞行高手？",
     "自然与生物", "技术直答",
     ["蜻蜓", "点水", "产卵", "复眼"], "通识拓展484·存量卡补题"),
    ("QB-1689", "鹦鹉为什么会学人说话？鹦鹉能理解语言吗？",
     "自然与生物", "技术直答",
     ["鹦鹉", "学舌", "鸣管", "模仿"], "通识拓展484·存量卡补题"),
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
                               "level:L2", "status:verified", "batch:通识拓展484"],
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
    bank["version"] = "v7.50"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
