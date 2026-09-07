# -*- coding: utf-8 -*-
"""seed_common_475_cards.py · 通识拓展批次475知识卡+题库（幂等）

475：3 张新卡·传统工艺三连（泥人面塑 kp_card_clayfigurine /
    景泰蓝 kp_card_cloisonne / 紫砂壶 kp_card_zisha）。
预检已过（QB-1660~1662 可用，三主题题库 0 覆盖、
卡库无同名专属卡——紫砂1张为误中已核实）。
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
    ("kp_card_clayfigurine",
     "泥人与面塑",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "泥人与面塑——指尖上的民间雕塑：①**泥人**——用黏土捏塑彩绘：天津"
     "「泥人张」（张明山开创，写实传神）、无锡惠山泥人（大阿福憨态可掬"
     "）是两大流派；②**面塑**——用蒸熟的面团加颜料捏塑人物花鸟，可食"
     "用可观赏，山东/山西/河南等地流行，俗称「捏面人」；③**工艺要点**"
     "——泥料要揉匀醒透防裂、阴干定型不可暴晒、彩绘在阴干后进行；④**"
     "题材**——戏曲人物、神话传说、市井生活、吉祥图案（年年有余/福禄"
     "寿）；⑤**地位**——泥人张彩塑、面塑均列入国家级非物质文化遗产。",
     ["泥人张是谁", "惠山泥人", "面塑是什么", "捏面人",
      "泥塑工艺流程", "民间雕塑"],
     ["问剪纸", "问皮影戏"],
     "atomic", "",
     "泥人面塑=黏土捏塑彩绘指尖雕塑+天津泥人张写实传神无锡惠山大阿福两"
     "大流派+面塑面团加颜料俗称捏面人山东山西河南流行+泥料揉匀醒透阴干"
     "定型彩绘最后+题材戏曲神话市井吉祥+泥人张面塑国家级非遗。"),
    ("kp_card_cloisonne",
     "景泰蓝",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "景泰蓝——铜胎掐丝珐琅器：①**得名**——明代景泰年间（1450-1457）"
     "工艺成熟且主流釉色为宝石蓝，故称「景泰蓝」；②**工艺流程**——制"
     "胎（铜胎）→掐丝（把细铜丝掐成图案粘在胎上）→点蓝（填入珐琅釉料"
     "）→烧蓝（高温烧制釉料熔化）→磨光→镀金，工序百余道；③**特点**"
     "——铜胎珐琅釉色彩艳丽持久、金丝勾勒轮廓富丽堂皇；④**历史**——"
     "工艺源自波斯，元朝传入中国，在明代与本土技艺融合达到巅峰；⑤**"
     "地位**——北京传统特种工艺品，列入国家级非物质文化遗产。",
     ["景泰蓝是什么", "景泰蓝名字的由来", "掐丝珐琅",
      "景泰蓝工艺流程", "点蓝烧蓝", "北京景泰蓝"],
     ["问瓷器", "问漆器"],
     "atomic", "",
     "景泰蓝=铜胎掐丝珐琅器明代景泰年间成熟釉色宝石蓝得名+制胎掐丝点蓝"
     "烧蓝磨光镀金百余道工序+珐琅釉艳丽持久金丝勾勒富丽+源自波斯元传入"
     "明融合巅峰+北京特种工艺国家级非遗。"),
    ("kp_card_zisha",
     "紫砂壶",
     "传统工艺知识点内容（人话接口）", "传统文化",
     "紫砂壶——江苏宜兴特产的紫砂陶茶具：①**材质**——宜兴特有的紫砂"
     "泥（紫泥/红泥/绿泥），含铁量高，双重气孔结构——透气不渗水，泡茶"
     "「隔夜不馊」；②**历史**——始于宋代，明清鼎盛；供春（明代）被"
     "尊为紫砂壶鼻祖；③**经典器型**——西施壶、石瓢壶、仿古壶、掇球"
     "壶等；④**为什么养壶**——长期泡茶壶体吸附茶汤形成温润「包浆」"
     "，越用越润——「一壶不侍二茶」让壶只泡一种茶味道纯正；⑤**地位**"
     "——宜兴紫砂陶制作技艺列入国家级非物质文化遗产。",
     ["紫砂壶是哪里的", "紫砂壶为什么好", "什么是包浆",
      "一壶不侍二茶", "供春壶", "宜兴紫砂"],
     ["问茶具", "问茶文化"],
     "atomic", "",
     "紫砂壶=宜兴紫砂泥含铁高双重气孔透气不渗水泡茶隔夜不馊+始于宋代"
     "明清鼎盛供春鼻祖+西施石瓢仿古掇球经典器型+养壶吸附茶汤成包浆越"
     "用越润一壶不侍二茶+宜兴紫砂陶制作技艺国家级非遗。"),
]

QUESTIONS = [
    ("QB-1660", "泥人张和惠山泥人各有什么特色？什么是面塑？",
     "传统文化", "技术直答",
     ["泥人", "面塑", "泥人张", "惠山"], "通识拓展475"),
    ("QB-1661", "景泰蓝的名字是怎么来的？它的制作工艺有哪些步骤？",
     "传统文化", "技术直答",
     ["景泰蓝", "掐丝珐琅", "点蓝", "烧蓝"], "通识拓展475"),
    ("QB-1662", "紫砂壶为什么泡茶好？什么是「包浆」？",
     "传统文化", "技术直答",
     ["紫砂壶", "宜兴", "包浆", "养壶"], "通识拓展475"),
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
                               "level:L2", "status:verified", "batch:通识拓展475"],
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
    bank["version"] = "v7.44"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
