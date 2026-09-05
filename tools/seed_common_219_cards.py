# -*- coding: utf-8 -*-
"""seed_common_219_cards.py · 通识拓展批次219知识卡+题库（幂等·两卡精批次）

219：生活常识-疣（瘊子）/生活常识-狐臭（腋臭）
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测
（HPV 加白名单）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_wart",
     "疣（瘊子）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "疣（俗称「瘊子」）=**HPV（人乳头瘤病毒）**感染皮肤引起的**良性**增生："
     "①**类型**——寻常疣（手部粗糙硬疙瘩）、跖疣（脚底，易与鸡眼混淆——跖"
     "疣捏痛按不痛、削开有小黑点[血栓血管]，鸡眼压痛）、扁平疣（青少年面部"
     "扁平小丘疹）；②**特性**——**自体接种扩散**（抠抓会把病毒带到别处长新"
     "疣——**别抠抓**）；约 **65% 的疣两年内可自行消退**（免疫清除）；③**治"
     "疗**——冷冻（液氮）/激光/水杨酸贴，反复需多次；④**预防**——不共用毛"
     "巾拖鞋、公共浴室穿拖鞋；HPV 疫苗可预防部分型别。疣是良性增生不会癌变"
     "（少数型别与宫颈病变相关是另一些 HPV 型别）。",
     ["瘊子是什么", "疣怎么治", "跖疣和鸡眼的区别", "疣会癌变吗",
      "扁平疣", "HPV疫苗预防疣"],
     ["问宫颈癌疫苗", "问鸡眼处理"],
     "atomic", "",
     "疣（瘊子）=HPV 感染皮肤良性增生：寻常疣/跖疣[捏痛压不痛有小黑点区别鸡眼压痛]/扁平疣；自体接种扩散勿抠抓；约 65% 两年内免疫自愈；治疗=冷冻激光水杨酸；不共用毛巾拖鞋公共浴室穿拖鞋防传染。"),
    ("kp_card_bodyodor",
     "狐臭（腋臭）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "狐臭=**大汗腺（顶泌汗腺）分泌物**被腋下细菌分解产生的不饱和脂肪酸气味"
     "（大汗腺集中在腋下/乳晕/外耳道——所以狐臭者常伴「油耳」）。**遗传决定"
     "**：**ABCC11 基因**的一个变异决定大汗腺分泌是否活跃——东亚人约 **90-"
     "95% 携带「干性耳垢+无狐臭」变异**，而欧美非裔多数没有——狐臭是「多数"
     "人有、我们少数人有」的正常体味变异，**不是病更不是不讲卫生**（洗得再干"
     "净腺体还在）。**应对**：轻度=止汗剂（氯化铝抑汗）+抗菌皂+剃腋毛减菌；"
     "重度=医疗手段（微波破坏大汗腺/手术）；青春期大汗腺才活跃，有人成年后"
     "减轻。去污名化：只是基因多样性。",
     ["狐臭是怎么回事", "腋臭怎么治", "狐臭遗传吗", "油耳和狐臭",
      "ABCC11基因", "狐臭手术"],
     ["问止汗剂选购", "问耳垢类型（干耳油耳）"],
     "atomic", "",
     "狐臭=大汗腺分泌物被腋下细菌分解的气味（大汗腺集中腋下乳晕外耳道——常伴油耳）；ABCC11 基因决定：东亚人 90-95% 携带无狐臭变异而欧美非裔多数有=正常基因多样非病非不讲卫生；轻度止汗剂抗菌皂剃腋毛，重度微波/手术。"),
]

QUESTIONS = [
    ("QB-861", "瘊子（疣）是什么引起的？为什么不能用手抠抓疣？", "生活常识", "技术直答",
     ["HPV", "病毒", "良性", "自体接种", "抠抓", "自愈"], "通识拓展219"),
    ("QB-862", "狐臭是怎么产生的？它与基因有什么关系？", "生活常识", "技术直答",
     ["大汗腺", "细菌分解", "ABCC11", "基因", "东亚", "油耳"], "通识拓展219"),
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
                               "level:L2", "status:verified", "batch:通识拓展219"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.90"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
