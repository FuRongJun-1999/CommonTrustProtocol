# -*- coding: utf-8 -*-
"""seed_common_209_cards.py · 通识拓展批次209知识卡+题库（幂等·两卡精批次）

209：生活常识-晕针晕血的机制与处理/生活常识-指甲白点辟谣
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（beekeeper 卡仅
「晕血」一词提及——血管迷走反射机制与蜂毒免疫划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_faint",
     "为什么会晕针晕血",
     "生活常识知识点内容（人话接口）", "生活常识",
     "晕针/晕血=**血管迷走神经反射**：恐惧/疼痛刺激→迷走神经过度兴奋→**心率"
     "减慢+血管扩张+血压骤降**→大脑短暂供血不足，出现面色苍白、出冷汗、眼前"
     "发黑、恶心，严重时短暂晕厥——**与过敏完全不同**（过敏=免疫系统反应，"
     "伴皮疹/呼吸困难）。**发生时处理**：立即**平卧+抬高下肢**（让血回流大"
     "脑）、松开领口，多数几分钟自行恢复。**预防**：采血/打针前**主动告知医"
     "护**（他们会让你躺着采、遮挡视线）；**别空腹**、前一天睡好；过程中**"
     "不看针头**、聊天分散注意、绷紧肌肉（肌肉泵促回流）。频繁晕厥者需就医"
     "排查心脏问题。",
     ["为什么会晕针", "晕血是怎么回事", "晕针怎么预防", "血管迷走神经反射",
      "晕血和过敏的区别", "抽血晕倒了怎么办"],
     ["问过敏性休克（用蜂毒卡划界）", "问空腹抽血项目"],
     "atomic", "",
     "晕针晕血=血管迷走神经反射（恐惧疼痛→心率血压骤降脑供血不足）：苍白冷汗眼前发黑可短暂晕厥，与过敏不同；处理=平卧抬腿松领口几分钟恢复；预防=告知医护躺着采+非空腹+不看针头绷紧肌肉；频繁晕厥查心脏。"),
    ("kp_card_nailspots",
     "指甲上的白点是什么",
     "基础科学知识点内容（人话接口）", "生物学",
     "指甲上的小白点（点状白甲）**不是缺钙缺锌**——这是流传最广的误传之一："
     "①**真相**——多为**甲床微小外伤**（磕碰/门夹/咬指甲/过度修剪）导致该处"
     "角化不全，形成小白点；**会随指甲生长向前移动**最终剪掉（观察它移动就是"
     "外伤证据——营养缺乏导致的白变化不会移动）；②白点与钙/锌无关（除非全"
     "身明确缺乏症）；③**需要留意的白变化**：**整个指甲变白**（可能肝病）、"
     "横向白色条纹（米氏线——某些中毒/重症的标志）、指甲变厚变黄变形（灰指"
     "甲=真菌）——单发小白点无需任何处理。",
     ["指甲上有白点是怎么回事", "指甲白点是缺钙吗", "点状白甲",
      "指甲白点会消失吗", "指甲白点缺什么"],
     ["问灰指甲（真菌）", "问指甲月牙（用月牙卡）"],
     "atomic", "",
     "指甲小白点=甲床微小外伤（磕碰/咬甲）致角化不全的点状白甲：会随指甲生长前移最终剪掉——「缺钙缺锌」是误传（营养性白变不移动）；整甲变白/米氏线/变厚变形才需就医查因；单发小白点无需处理。"),
]

QUESTIONS = [
    ("QB-843", "抽血时为什么会晕针晕血？发生了应该怎么处理？", "生活常识", "技术直答",
     ["血管迷走神经", "反射", "血压", "平卧", "抬腿", "过敏区别"], "通识拓展209"),
    ("QB-844", "指甲上出现小白点是缺钙缺锌吗？这些白点会消失吗？", "生物学", "技术直答",
     ["外伤", "误传", "随指甲", "前移", "角化", "缺钙"], "通识拓展209"),
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
                               "level:L2", "status:verified", "batch:通识拓展209"],
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
    bank["version"] = "v4.81"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
