# -*- coding: utf-8 -*-
"""seed_common_184_cards.py · 通识拓展批次184知识卡+题库（幂等·两卡精批次）

184：生活常识-冰淇淋头痛/生物学-延迟性肌肉酸痛（DOMS）
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（乳酸老卡讲概念，
本卡讲 DOMS 机制纠正「乳酸堆积」误区；mpemba 卡仅冰淇淋一词提及）。
执行前外文长词检测（DOMS 加白名单）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_icecreamhead",
     "冰淇淋头痛",
     "生活常识知识点内容（人话接口）", "生活常识",
     "大口吃冰淇淋/猛灌冰饮后**前额或太阳穴剧痛**几秒到半分钟（「脑结冰」）="
     "**冰淇淋头痛**：①机制——冰冷刺激**上颚与咽喉后壁**，局部血管先急剧收缩"
     "再反射性扩张，**三叉神经**把疼痛信号误传到前额（牵涉痛——痛的位置不在"
     "受刺激处）；②**特点**：快速吃冷食、天热运动后猛喝冰饮、偏头痛体质者更"
     "易发生；③**缓解**：停止吃冷物、舌尖**抵上颚**给局部「回暖」、低头片刻"
     "——通常 30 秒内自行消退，**无害**；④**就医线**：头部剧痛突然发作且持"
     "续不缓解、伴呕吐视物模糊/肢体麻木=不是冰淇淋头痛，立即就医（排查脑血管"
     "问题）。小技巧：小口慢吃、让冷食在口腔前端稍作停留升温再咽，即可享受又"
     "不痛。",
     ["吃冰淇淋头痛怎么回事", "脑结冰", "冰淇淋头痛的原因",
      "吃冰的为什么会头疼", "三叉神经"],
     ["问偏头痛管理（就医）", "问冷饮与健康"],
     "atomic", "",
     "冰淇淋头痛（脑结冰）=冰冷刺激上颚→血管急缩急扩+三叉神经牵涉痛传到前额（几秒到半分钟自限无害）；缓解=停冷食+舌尖抵上颚回暖+小口慢吃；剧痛持续伴呕吐麻木=脑血管问题立即就医。"),
    ("kp_card_doms",
     "延迟性肌肉酸痛（DOMS）",
     "基础科学知识点内容（人话接口）", "生物学",
     "运动后**第二天起**才出现的肌肉酸痛=**延迟性肌肉酸痛（DOMS）**，一般 "
     "24-72 小时达到高峰、5-7 天消退。**机制已更新**：不是「乳酸堆积」——乳"
     "酸在运动后 1-2 小时内就代谢完毕；真正原因是**不习惯的运动（尤其离心收"
     "缩如下坡跑、缓慢下放）造成肌纤维微损伤**+局部炎症反应，修复过程释放致"
     "痛物质并使肌肉对疼痛敏感。**处理**：①轻中度活动（散步/游泳）反而缓解"
     "（促进血流）；②充足蛋白质+睡眠助修复；③轻度拉伸；④**勿加大强度硬练**"
     "（损伤期加重伤）。**预防**：循序渐进加量（每周增幅≤10%）、运动前充分热"
     "身。说明：DOMS 与扭伤不同——若**急性锐痛/关节肿胀/活动受限**是急性损"
     "伤，按扭伤处理（RICE）。",
     ["运动后肌肉酸痛为什么延迟", "DOMS是什么", "乳酸堆积是谣言吗",
      "肌肉酸痛还能练吗", "延迟性肌肉酸痛怎么缓解"],
     ["问运动损伤RICE（用RICE卡）", "问运动后拉伸"],
     "atomic", "",
     "DOMS=延迟性肌肉酸痛 24-72h 高峰 5-7 天消退：肌纤维微损伤+炎症修复（乳酸 1-2h 已代谢，堆积论过时）；处理=轻活动促血流+蛋白+睡眠，勿硬练；预防=渐进负荷每周≤10%；急性锐痛肿胀=扭伤按 RICE。"),
]

QUESTIONS = [
    ("QB-796", "大口吃冰淇淋后前额剧痛（冰淇淋头痛）是怎么回事？怎么快速缓解？", "生活常识", "技术直答",
     ["血管", "收缩", "三叉神经", "牵涉痛", "上颚", "自愈"], "通识拓展184"),
    ("QB-797", "运动后第二天才出现的肌肉酸痛是什么？「乳酸堆积」的说法对吗？", "生物学", "技术直答",
     ["DOMS", "延迟性", "微损伤", "炎症", "乳酸", "1-2小时"], "通识拓展184"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
                 "effect", "Additives", "DOMS"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
                problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


def ensure_seed() -> dict:
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
                               "level:L2", "status:verified", "batch:通识拓展184"],
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

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.57"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
