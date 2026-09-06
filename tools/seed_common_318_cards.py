# -*- coding: utf-8 -*-
"""seed_common_318_cards.py · 通识拓展批次318知识卡+题库（幂等）

318：建筑-斗拱与榫卯/建筑-应县木塔与《营造法式》（中国古建新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1193/1194+双id可用）。
注：赵州桥已有 QB-122，本批避让。
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
             "BCS", "B2H6", "borrow", "Rust"}


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
    ("kp_card_dougong2",
     "斗拱与榫卯",
     "建筑通识知识点内容（人话接口）", "历史",
     "中国古建两大绝技：①**榫卯**——木构件凸（榫）凹（卯）咬合连接，"
     "不用一根钉子；柔性连接让地震能量被节点变形吸收（柔性抗震），拆装"
     "可逆（可维修可迁移）；②**斗拱**——柱顶层层出挑的斗形木构件+弓形"
     "肘木（斗+拱+昂），三大作用：把屋顶重量传到柱身（传力）、挑出屋檐"
     "（深远出檐保护墙身）、装饰等级（斗拱层数=建筑等级，明清后装饰化）；"
     "③**抗震实证**——应县木塔（1056 年，67 米全木）历经多次大地震与"
     "战火炮击千年不倒，现代振动台实验惊人稳固；④**模数制度**——宋代"
     "《营造法式》（1103 年）确立「材分制」（以斗拱断面为基准模数），"
     "设计与预算标准化——世界最早的建筑标准化文献之一；⑤**现状**——"
     "传统大木作技艺列入非遗，古建修缮依赖老匠师传帮带。",
     ["斗拱是什么", "榫卯为什么不用钉子", "应县木塔为什么千年不倒",
      "营造法式是什么", "斗拱的作用", "柔性抗震"],
     ["问古建修缮", "问吊脚楼"],
     "atomic", "",
     "斗拱榫卯=凸凹咬合无钉柔性连接吸震+斗拱传力挑檐标等级+应县木塔"
     "1056年67米千年不倒实证+营造法式1103材分制模数标准化世界最早+"
     "大木作技艺非遗。"),
    ("kp_card_yingxianta",
     "应县木塔与《营造法式》",
     "建筑历史知识点内容（人话接口）", "历史",
     "应县木塔——世界现存最高的古代木结构建筑：①**基本盘**——辽代 1056"
     " 年建（佛宫寺释迦塔），高约 67 米（相当于 20 层楼），全木榫卯无钉"
     "无铆，用红松木料约 3000 立方米、重约 2600 吨；②**结构奇迹**——"
     "双套筒式（内外槽）+54 种斗拱集大成（「斗拱博物馆」）+多层刚性圈梁"
     "与柔性柱础结合——历 40 余次地震、200 余发炮击、多次雷击仍屹立 967"
     " 年；③**倾斜之忧**——二层柱倾斜加剧（近年监测治理争议：落架大修"
     "vs 原状加固），保护难题世界级；④**《营造法式》**——北宋 1103 年"
     "颁行（李诫编），中国第一部建筑规范：材分模数制（斗拱「材」为基准"
     "按比例算料）+工料定额（防贪墨）+图样（最早的建筑工程图）；⑤**"
     "对比**——《营造法式》比欧洲同类的建筑规范图籍早约 600 年。",
     ["应县木塔多少年历史", "应县木塔为什么不倒",
      "营造法式是谁编的", "释迦塔", "材分制", "木塔倾斜"],
     ["问古建测绘", "问佛塔演变"],
     "atomic", "",
     "应县木塔=辽1056年佛宫寺释迦塔67m全木榫卯3000m³2600吨+双套筒54种"
     "斗拱刚柔并济+历40余震200发炮击967年屹立+二层倾斜治理世界难题+"
     "营造法式1103李诫材分模数工料定额早欧洲600年。"),
]

QUESTIONS = [
    ("QB-1193", "斗拱和榫卯在中国古建筑中起什么作用？", "历史", "技术直答",
     ["榫卯", "斗拱", "抗震", "等级"], "通识拓展318"),
    ("QB-1194", "应县木塔为什么能千年不倒？《营造法式》是什么书？", "历史", "技术直答",
     ["应县木塔", "斗拱", "营造法式", "材分"], "通识拓展318"),
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
                               "level:L2", "status:verified", "batch:通识拓展318"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.88"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
