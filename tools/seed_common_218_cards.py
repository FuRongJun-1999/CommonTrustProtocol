# -*- coding: utf-8 -*-
"""seed_common_218_cards.py · 通识拓展批次218知识卡+题库（幂等·两卡精批次）

218：生活常识-荨麻疹/生活常识-正确测血压
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（homekit 仅急救药
提及、salt 卡讲高血压饮食——测量方法角度划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_urticaria",
     "荨麻疹（风团）",
     "生活常识知识点内容（人话接口）", "生活常识",
     "荨麻疹（风团/风疙瘩）=皮肤黏膜**组胺释放**引起的过敏性皮肤病：①**典型"
     "表现**——高出皮面的**苍白色或粉红色风团**、剧烈瘙痒、**此起彼伏**（一处"
     "消退另一处又起，单个风团 24 小时内消退不留痕）；②**诱因**——食物（海"
     "鲜/酒精）、药物、感染、冷热刺激（寒冷性荨麻疹）、压力摩擦（皮肤划痕"
     "症——指甲一划就起条状凸起）；③**处理**——口服**抗组胺药**（氯雷他定/"
     "西替利嗪，第二代不嗜睡）、冷敷止痒、避免搔抓与热刺激；④**急诊信号**——"
     "**喉头水肿**（喉咙发紧/声音嘶哑/呼吸困难）或过敏性休克（头晕血压降）"
     "——立即 120+肾上腺素。**慢性荨麻疹**（超 6 周）多数查不出明确过敏原，"
     "规律用药控制为主。",
     ["荨麻疹是什么", "荨麻疹怎么引起的", "风团是什么", "荨麻疹怎么治疗",
      "荨麻疹会传染吗", "胆碱能性荨麻疹"],
     ["问过敏原检测", "问湿疹（用湿疹卡）"],
     "atomic", "",
     "荨麻疹（风团）=组胺释放过敏性皮肤病：粉白风团剧痒此起彼伏 24h 消退不留痕；诱因=海鲜酒精药物冷热压力；处理=二代抗组胺药氯雷他定西替利嗪+冷敷；急诊信号=喉头水肿呼吸困难过敏性休克 120；慢性超 6 周多查不出过敏原规律用药。"),
    ("kp_card_bpguide",
     "在家测血压的正确方法",
     "生活常识知识点内容（人话接口）", "生活常识",
     "家庭自测血压要点：①**设备**——选**上臂式电子血压计**（腕式/手指式误差"
     "大不推荐）；②**测前准备**——安静休息 **5 分钟**、测前 30 分钟不喝咖啡/"
     "浓茶/吸烟、排空膀胱；③**姿势**——坐位背有依靠、袖带与**心脏同一水"
     "平**、袖带下缘距肘窝 2-3cm、双脚平放不跷腿、测时不说话；④**读数**——"
     "高血压诊断参考：诊室 ≥140/90mmHg、**家庭自测 ≥135/85mmHg**；⑤**规律"
     "测**——初测或调药期早晚各一次连续 7 天，稳定后每周 1-2 次；记录数值"
     "供医生参考。**注意**：第一次测两臂都测，以读数高的一侧为准；血压计定期"
     "校准。",
     ["在家测血压的正确方法", "血压计选腕式还是臂式", "测血压前注意什么",
      "高血压标准是多少", "家庭自测血压", "袖带位置"],
     ["问高血压用药（就医）", "问盐与血压（用盐卡）"],
     "atomic", "",
     "家庭测血压=上臂式电子血压计+测前静坐 5 分钟30 分钟内勿咖啡烟+袖带与心脏同高水平+不说话跷腿；家庭标准 ≥135/85（诊室 140/90）；早晚各一次连续 7 天稳定后每周 1-2 次记录供医生；首测双臂取高侧。"),
]

QUESTIONS = [
    ("QB-859", "荨麻疹的典型表现是什么？出现哪些信号需要立即就医？", "生活常识", "技术直答",
     ["风团", "瘙痒", "组胺", "抗组胺药", "喉头水肿", "120"], "通识拓展218"),
    ("QB-860", "在家测血压的正确方法是什么？家庭自测的高血压标准是多少？", "生活常识", "技术直答",
     ["上臂式", "静坐", "5分钟", "心脏同高", "135/85", "140/90"], "通识拓展218"),
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
                               "level:L2", "status:verified", "batch:通识拓展218"],
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
    bank["version"] = "v4.89"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
