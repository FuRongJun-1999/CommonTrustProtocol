# -*- coding: utf-8 -*-
"""seed_common_168_cards.py · 通识拓展批次168知识卡+题库（幂等·两卡精批次）

168：生物学-动物冬眠/地理学-温泉与地热
KCCS 四要素+题干原句触发词。三重预检：冬眠双库零覆盖；温泉（fossilfuel 仅
提「地热」能源词）主题未覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hibernate",
     "动物冬眠",
     "基础科学知识点内容（人话接口）", "生物学",
     "冬眠=动物**主动降低代谢**越冬的策略：心率呼吸骤减（刺猬从每分钟 200 次"
     "降到个位数）、体温大幅下降（真冬眠者可接近 0-5°C）、靠**入冬前囤积的脂"
     "肪**缓慢供能度过食物匮乏的冬天。①**真冬眠者**：地松鼠、刺猬、仓鼠、蝠"
     "——体温降至接近环境温度，深度的「麻痹」状态；②**冬眠界的误会——熊不"
     "算真冬眠**：熊的体温只降几度、易被惊醒（属「冬蛰/深睡眠」），母熊还能在"
     "此期间产崽哺乳；③**变温动物**（蛇/蛙/龟）体温随环境走，冬天进入**冬蛰"
     "**（僵冷不动，非主动调温）；④**周期性苏醒**：真冬眠者每隔数日到数周会"
     "短暂升温苏醒——喝水排泄、清除代谢废物（睡眠债务假说），并非一睡到底；⑤"
     "唤醒耗能巨大——冬眠中被反复打扰可能致命（**别打扰冬眠的动物**）。冷知"
     "识：科学家研究冬眠机制用于低温医疗与长期太空飞行的可能性。",
     ["哪些动物会冬眠", "熊冬眠吗", "冬眠的动物体温", "为什么动物要冬眠",
      "冬眠会被吵醒吗"],
     ["问动物迁徙（用迁徙卡）", "问人类低温休眠技术"],
     "atomic", "",
     "冬眠=主动降代谢越冬：真冬眠者(地松鼠刺猬仓鼠)体温近环境+心率骤减靠囤脂供能；熊只降几度易惊醒=冬蛰深睡眠非真冬眠；变温动物蛇蛙为僵冷冬蛰；周期性苏醒排废物——打扰冬眠动物可能致命。"),
    ("kp_card_hotspring",
     "温泉是怎么形成的",
     "人文通识知识点内容（人话接口）", "地理学",
     "温泉=**地下热水自然涌出地表**：①**热源**——地壳越深越热（地热梯度约每"
     "公里升温 25-30°C），地下水下渗到深处被**岩浆余热/地热梯度**加热（火山"
     "区温泉最热最集中）；②**通道与承压**——热水密度小沿裂隙**上升**，涌出"
     "地表即温泉（若被封存则为热水井）；③**矿物质**——加热过程溶入矿物成分"
     "：含硫泉（「臭鸡蛋」味硫化氢，助皮肤病）、碳酸泉（冒泡「气泡汤」）、铁"
     "泉（锈色）等，日本「泉质分类」即按成分；④**中国温泉大省**：台湾（大屯"
     "火山）、云南（腾冲热海——97°C 沸泉「大滚锅」）、西藏（羊八井——既发电"
     "又供暖，地热发电示范）。**泡泉注意**：一次 15-20 分钟起身休息（高温血"
     "管扩张易头晕）、空腹/酒后/饭后 1 小时内勿泡、高血压心脏病者谨慎、泉温"
     "42°C 以上尤其当心。",
     ["温泉是怎么形成的", "温泉水为什么是热的", "泡温泉要注意什么",
      "腾冲大滚锅", "羊八井地热", "温泉含硫有什么用"],
     ["问地热发电原理", "问火山分布"],
     "atomic", "",
     "温泉=地下水被地热梯度/岩浆余热加热后沿裂隙承压涌出：硫泉/碳酸泉/铁泉按成分分类；台湾云南腾冲大滚锅 97°C/西藏羊八井地热发电；泡泉 15-20 分钟起身、空腹酒后勿泡、心脑血管谨慎。"),
]

QUESTIONS = [
    ("QB-757", "哪些动物会真正冬眠？熊的冬眠和刺猬的冬眠有什么不同？", "生物学", "技术直答",
     ["地松鼠", "刺猬", "体温", "深睡眠", "冬蛰", "代谢"], "通识拓展168"),
    ("QB-758", "温泉的水为什么是热的？泡温泉有什么注意事项？", "地理学", "技术直答",
     ["地热", "岩浆", "地下水", "15-20分钟", "酒后", "通风"], "通识拓展168"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
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
                               "level:L2", "status:verified", "batch:通识拓展168"],
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
    bank["version"] = "v4.41"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
