# -*- coding: utf-8 -*-
"""seed_common_407_cards.py · 通识拓展批次407知识卡+题库（幂等）

407：3 张新卡·中国神话寓言三连（盘古开天与女娲造人 kp_card_creation /
    后羿射日与嫦娥奔月 kp_card_houyi / 愚公移山与精卫填海
    kp_card_yugong）。与航天探月主题（kp_card_spaceexp，已有 QB-565）
    明确区分。预检已过（QB-1459~1461 可用，三主题题库卡库双零）。
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
    ("kp_card_creation",
     "盘古开天与女娲造人",
     "中国神话知识点内容（人话接口）", "传统文化",
     "中国创世神话的两大主角：①**盘古开天辟地**——宇宙初始混沌如鸡蛋，"
     "盘古孕育其中一万八千年，醒来挥斧分开天地：轻清之气上升为天，重浊"
     "之气下沉为地；盘古死后垂身化万物——气成风云、声为雷霆、左眼为日、"
     "右眼为月、四肢五体化为四极五岳（记载见于《三五历纪》）；②**女娲"
     "造人补天**——女娲抟黄土捏人（后用藤条甩泥浆批量造人），让大地有"
     "了人类；共工怒触不周山撞塌天柱后，女娲炼五色石补苍天、断鳌足立"
     "四极，拯救世界（《淮南子》《风俗通义》）；③**文化意义**——创世"
     "神话解释「世界与人从哪来」，盘古的奉献与女娲的创造力成为中国"
     "文化中牺牲精神与创造精神的源头意象。",
     ["盘古开天的故事", "女娲造人的传说", "女娲补天",
      "中国创世神话", "盘古为什么要开天", "不周山"],
     ["问后羿射日", "问希腊神话"],
     "atomic", "",
     "盘古开天女娲造人=混沌如鸡子盘古万八千年挥斧分天地轻清为天重浊为"
     "地垂死化身日月风云五岳+女娲抟土造人藤条甩泥+共工触不周天塌女娲"
     "炼五色石补天断鳌足立极+见于三五历纪淮南子+牺牲与创造精神源头。"),
    ("kp_card_houyi",
     "后羿射日与嫦娥奔月",
     "中国神话知识点内容（人话接口）", "传统文化",
     "一对紧紧相联的上古神话：①**后羿射日**——远古时十日并出，晒焦庄"
     "稼草木，民不聊生；神射手后羿弯弓搭箭射落九日、留下一日按时起落，"
     "拯救苍生（《淮南子》记载）；②**嫦娥奔月**——后羿从西王母处得不"
     "死药，交给嫦娥保管；流传最广的版本是坏人蓬蒙趁后羿外出逼药，嫦娥"
     "情急吞药飞升月宫，居广寒宫；后羿思念妻子，在院中摆上她爱吃的果品"
     "遥祭——民间中秋拜月的习俗与此相关；月宫里还有玉兔捣药、吴刚伐桂"
     "的意象；③**文化意义**——射日是人定胜天的抗争精神，奔月把月亮"
     "变成中国人的浪漫符号（探月工程以嫦娥命名正是呼应）。",
     ["后羿射日的故事", "嫦娥为什么奔月", "嫦娥和后羿什么关系",
      "广寒宫玉兔", "中秋和嫦娥的关系", "十日并出"],
     ["问吴刚伐桂", "问中国神话"],
     "atomic", "",
     "后羿射日嫦娥奔月=十日并出草木焦枯后羿射落九日救苍生+嫦娥吞不死"
     "药飞升月宫广寒宫蓬蒙逼药版本流传最广+玉兔捣药吴刚伐桂+中秋拜月"
     "习俗关联+人定胜天抗争精神与月亮浪漫符号探月工程嫦娥命名呼应。"),
    ("kp_card_yugong",
     "愚公移山与精卫填海",
     "中国寓言知识点内容（人话接口）", "传统文化",
     "两个「以微小之力对抗巨大困难」的经典寓言：①**愚公移山**——《列"
     "子·汤问》：九十岁的愚公嫌太行、王屋二山挡路，率子孙挖山；智叟"
     "讥笑他自不量力，愚公答「我死了有儿子，儿子还有孙子，子子孙孙无"
     "穷匮也，而山不加增」；天帝被感动，派神把山背走——赞坚韧不拔、"
     "着眼长远的恒心；②**精卫填海**——《山海经》：炎帝的小女儿溺亡于"
     "东海，化为精卫鸟，日复一日衔西山木石填东海——明知不可能仍不放弃"
     "的不屈意志；③**共同精神**——面对看似不可能的困难，强调意志与"
     "坚持的力量；两条成语至今用来形容持之以恒的奋斗；④**对比**——"
     "「夸父追日」同属抗争型神话但结局是渴死道中，寓言常与「不自量力」"
     "辨析：寓言肯定的是精神，不是蛮干。",
     ["愚公移山的故事", "愚公移山出自哪本书", "精卫填海的含义",
      "精卫是谁", "子子孙孙无穷匮也", "坚持不懈的寓言"],
     ["问中国神话", "问成语典故"],
     "atomic", "",
     "愚公移山精卫填海=列子汤问太行王屋二山子子孙孙无穷匮而山不加增"
     "天帝派神搬山+山海经炎帝之女溺东海化精卫衔石填海+微小之力抗巨大"
     "困难恒心与不屈+成语形容持之以恒+肯定精神非蛮干。"),
]

QUESTIONS = [
    ("QB-1459", "盘古开天辟地讲了什么？女娲为什么补天？",
     "传统文化", "技术直答",
     ["盘古", "女娲", "开天", "补天"], "通识拓展407"),
    ("QB-1460", "后羿射日和嫦娥奔月是什么故事？和中秋节有什么关系？",
     "传统文化", "技术直答",
     ["后羿", "嫦娥", "奔月", "中秋"], "通识拓展407"),
    ("QB-1461", "愚公移山和精卫填海讲了什么道理？分别出自哪本书？",
     "传统文化", "技术直答",
     ["愚公移山", "精卫填海", "坚持", "寓言"], "通识拓展407"),
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
                               "level:L2", "status:verified", "batch:通识拓展407"],
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
    bank["version"] = "v6.78"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
