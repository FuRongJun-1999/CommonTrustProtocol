# -*- coding: utf-8 -*-
"""seed_common_208_cards.py · 通识拓展批次208知识卡+题库（幂等·两卡精批次）

208：生活常识-久蹲站起眼前发黑/生活常识-黑眼圈的三种类型
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（磨牙/脚麻弱关联弃）。
执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_orthostatic",
     "久蹲站起为什么会眼前发黑",
     "生活常识知识点内容（人话接口）", "生活常识",
     "蹲久了猛站起来**眼前发黑、头晕**=**体位性（直立性）低血压**的正常生理"
     "反应：①蹲着时下肢血管被压，血液淤积在下半身；②猛站起时**重力使血液来"
     "不及回流**，大脑短暂供血不足→眼前发黑；③几秒内身体反射调节（心跳加快/"
     "血管收缩）后恢复。**预防**：起身**缓慢**——先低头、扶物、分步站起；平"
     "时多喝水、规律运动改善血管调节。**警惕线**：发黑持续时间长（>10 秒）、"
     "**真的晕倒**、伴心悸胸闷，或在没有快速起身时也频繁发作——排查贫血、低"
     "血糖、心律失常等（不是所有头晕都是「蹲多了」）。",
     ["蹲久了站起来眼前发黑", "体位性低血压", "起身头晕怎么回事",
      "蹲下猛站起来头晕", "眼前发黑要警惕什么"],
     ["问贫血检查（就医）", "问颈椎头晕鉴别（就医）"],
     "atomic", "",
     "久蹲站起眼前发黑=体位性低血压（血液淤积下肢回心血量骤减脑短暂供血不足）——正常生理几秒恢复；预防=起身缓慢分步+多喝水规律运动；警惕=发黑>10 秒/真晕倒/伴心悸或非快速起身也发作→排查贫血心律问题。"),
    ("kp_card_darkcircle",
     "黑眼圈的三种类型",
     "生活常识知识点内容（人话接口）", "生活常识",
     "黑眼圈不是都是熬夜熬的——分三型，护理方向完全不同：①**血管型（青紫"
     "色）**——眼周皮肤薄+血液循环差（熬夜/疲劳/鼻炎鼻塞加重）：热敷、规律"
     "作息、治鼻炎能改善；轻拉下眼睑颜色**变深**=血管型；②**色素型（棕褐"
     "色）**——日晒/摩擦/遗传导致黑色素沉积（揉眼越揉越黑）：**防晒**+含美"
     "白成分眼霜、**戒揉眼**；③**结构型（阴影）**——泪沟凹陷/眼袋凸出形成的"
     "阴影：轻拉下眼睑颜色**不变**、换个角度光线阴影移动=结构型，需医美填充"
     "或手术改善。自测法：轻拉下眼皮肤向下轻拉——颜色变浅=血管型，不变=色素"
     "或结构型。熬夜只是血管型的加重因素之一——「早睡」不能解决所有黑眼圈。",
     ["黑眼圈是怎么回事", "黑眼圈分几种类型", "血管型黑眼圈",
      "黑眼圈怎么去除", "熬夜和黑眼圈的关系"],
     ["问医美填充（自行评估）", "问鼻炎与眼周循环"],
     "atomic", "",
     "黑眼圈三型=血管型(青紫·循环差熬夜鼻炎·热敷作息)+色素型(棕褐·日晒摩擦·防晒戒揉)+结构型(泪沟眼袋阴影·需医美)；自测=轻拉下睑变浅为血管型不变为色素/结构；熬夜只是血管型加重因素之一。"),
]

QUESTIONS = [
    ("QB-841", "蹲久了猛站起来为什么会眼前发黑？出现哪些情况需要就医检查？", "生活常识", "技术直答",
     ["体位性低血压", "血液", "回流", "缓慢", "晕倒", "贫血"], "通识拓展208"),
    ("QB-842", "黑眼圈分为哪三种类型？为什么说早睡不能解决所有黑眼圈？", "生活常识", "技术直答",
     ["血管型", "色素型", "结构型", "防晒", "泪沟", "熬夜"], "通识拓展208"),
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
                               "level:L2", "status:verified", "batch:通识拓展208"],
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
    bank["version"] = "v4.80"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
