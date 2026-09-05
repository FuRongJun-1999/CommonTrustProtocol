# -*- coding: utf-8 -*-
"""seed_common_177_cards.py · 通识拓展批次177知识卡+题库（幂等·两卡精批次）

177：生活常识-冻疮/生活常识-口臭的来源
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_chilblain",
     "冻疮",
     "生活常识知识点内容（人话接口）", "生活常识",
     "冻疮≠冻伤：冻疮是寒冷（0-10°C）**加潮湿**环境下，手指/脚趾/耳廓/鼻尖"
     "等末梢血管**收缩-扩张反复**导致的局限性炎症——红紫肿胀、**痒和痛**（尤"
     "其遇热后奇痒）。**高危**：末梢循环差者、女性儿童多见、手足多汗（潮湿加"
     "速散热）。**处理**：①**温水复温**（37-40°C 温水浸泡，逐渐回暖）；②**"
     "切勿火烤/热水烫/雪搓**——受冻组织感觉迟钝易烫伤，骤热加重组织损伤（这"
     "是流传最广的错误做法）；③可涂多磺酸粘多糖乳膏等促循环药膏，破溃感染需"
     "就医；④**预防大于治疗**——手脚保暖干燥（手套/干鞋袜，汗湿即换）、坚持"
     "运动促末梢循环、入冬前开始用温水+冷水交替洗手锻炼血管调节能力（每年发"
     "作的人可在初秋开始）。",
     ["冻疮怎么处理", "冻疮痒怎么办", "冻疮能用热水烫吗", "冻疮和冻伤的区别",
      "冻疮每年复发", "耳朵长冻疮"],
     ["问严重冻伤急救（就医）", "问雷诺现象（就医排查）"],
     "atomic", "",
     "冻疮=0-10°C+潮湿下末梢血管收缩扩张反复的炎症（红紫肿·遇热奇痒）：温水 37-40°C 复温+多磺酸粘多糖膏；切勿火烤热水烫雪搓（感觉迟钝易二次损伤）；预防=保暖干燥+运动促循环+初秋温冷水交替锻炼。"),
    ("kp_card_badbreath",
     "口臭的来源",
     "生活常识知识点内容（人话接口）", "生活常识",
     "口臭约 **90% 源自口腔本身**，不是「肠胃不好」：①**口腔来源（主因）**"
     "——舌苔（舌背乳头间厌氧菌分解食物残渣与蛋白质，产生挥发性硫化物=臭味"
     "主力）、牙周炎与牙龈炎（牙周袋藏菌）、龋齿洞、智齿冠周炎、假牙清洁不"
     "当；②**晨起口臭**属正常（睡眠唾液分泌少，细菌繁殖增多，刷牙即消）；③"
     "**非口腔来源**（少数）：鼻窦炎/扁桃体结石、胃食管反流、糖尿病（烂苹果"
     "味酮味——提示酮症酸中毒要警惕）、肝肾疾病特殊气味；④**应对**：刷牙+**"
     "刷舌苔**（大部分人口臭主源）+牙线清洁牙缝+半年洗牙；多喝水防口干；治"
     "好牙周病口臭多随之消失。**误区**：嚼口香糖只是掩盖；「幽门螺杆菌是口"
     "臭主因」被夸大——真正由胃产生的口臭是少数。",
     ["口臭是什么原因", "口臭怎么根治", "刷舌苔有必要吗",
      "肠胃不好会口臭吗", "幽门螺杆菌口臭", "扁桃体结石口臭"],
     ["问牙周病治疗", "问幽门螺杆菌检测"],
     "atomic", "",
     "口臭 90% 源自口腔：舌苔厌氧菌产硫化物（主源）+牙周炎龋齿智齿冠周炎；晨起口臭正常刷完即消；少数来自鼻窦/扁桃体结石/反流/糖尿病酮味；应对=刷牙+刷舌苔+牙线+洗牙；幽门螺杆菌口臭主因说被夸大。"),
]

QUESTIONS = [
    ("QB-781", "长了冻疮能用热水烫或火烤吗？正确的处理和预防方法是什么？", "生活常识", "技术直答",
     ["温水", "复温", "切勿", "火烤", "潮湿", "保暖"], "通识拓展177"),
    ("QB-782", "口臭的主要来源是肠胃还是口腔？应该如何应对口臭问题？", "生活常识", "技术直答",
     ["口腔", "舌苔", "牙周", "硫化物", "90%", "刷舌苔"], "通识拓展177"),
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
                               "level:L2", "status:verified", "batch:通识拓展177"],
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
    bank["version"] = "v4.50"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
