# -*- coding: utf-8 -*-
"""seed_common_200_cards.py · 通识拓展批次200知识卡+题库（幂等·单卡+复测锚定）

200：生活常识-手指倒刺（里程碑批次：出卡+第三次随机复测锚定）
KCCS 四要素+题干原句触发词。三重预检：倒刺双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hangnail",
     "手指倒刺",
     "生活常识知识点内容（人话接口）", "生活常识",
     "倒刺（逆剥）=指甲旁的角质层**干燥翘起撕裂**形成的小片皮肤：①**成因**——"
     "「缺维生素」的说法**不科学**：主因是**局部干燥+物理摩擦**（洗手多/洗洁"
     "精/啃咬撕扯/美甲化学刺激）；②**正确处理**：温水或温水泡软后，用**干净"
     "指甲剪齐根剪掉**，再涂护手霜/指缘油保湿；③**千万别撕！**——撕扯会把倒"
     "刺往甲床深处撕开，造成开放伤口→**甲沟炎**（红肿化脓，严重需拔甲）；④**"
     "预防**：做家务戴手套、洗后即涂护手霜、指缘油定期涂、改掉啃手指习惯。"
     "已红肿化脓的甲沟炎需就医（可能需引流或抗生素）。",
     ["手指长倒刺怎么办", "倒刺是缺维生素吗", "倒刺为什么不能撕",
      "甲沟炎", "倒刺怎么处理"],
     ["问指甲月牙（用月牙卡）", "问甲沟炎治疗（就医）"],
     "atomic", "",
     "倒刺=甲周角质干燥翘起（主因干燥+摩擦，「缺维生素」说法不科学）；处理=温水泡软齐根剪+护手霜指缘油保湿；切勿撕扯——撕深破口致甲沟炎化脓；做家务戴手套+改掉啃咬。"),
]

QUESTIONS = [
    ("QB-828", "手指长倒刺是因为缺维生素吗？为什么倒刺不能直接撕掉？", "生活常识", "技术直答",
     ["干燥", "摩擦", "缺维生素", "不科学", "撕", "甲沟炎"], "通识拓展200"),
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
                               "level:L2", "status:verified", "batch:通识拓展200"],
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
    bank["version"] = "v4.73"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
