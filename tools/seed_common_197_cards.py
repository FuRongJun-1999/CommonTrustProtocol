# -*- coding: utf-8 -*-
"""seed_common_197_cards.py · 通识拓展批次197知识卡+题库（幂等·两卡+触发词补强）

197：生活常识-粉刺黑头护理/生活常识-脱发的类型与应对
+ 触发词补强：fishbone/ulcer 两卡生效条件补口语短触发变体（短触发复测缺口）。
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
    ("kp_card_acnecare",
     "粉刺与黑头的护理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "粉刺黑头=**痤疮（青春痘）的早期形态**：毛孔被皮脂+角质混合物堵塞——闭"
     "口粉刺（白头，闭口）与开放粉刺（**黑头**：油脂氧化变黑，不是脏东西没洗"
     "净）。**护理**：①温和清洁早晚各一次（过度清洁刺激出更多油）；②**含水"
     "杨酸/阿达帕林**的产品疏通角质（夜间用、建立耐受）；③**别用手挤**（炎"
     "症+痘坑痘印——挤黑头撕拉鼻贴也伤毛孔）；④防晒（紫外线加重色沉）；⑤"
     "饮食：高糖高奶（乳清蛋白）与痤疮相关证据较强。**就医线**：中重度痤疮（"
     "脓包/囊肿结节）看皮肤科——外用过氧化苯甲酰/口服药需医生处方，痘坑越早"
     "干预越好。",
     ["粉刺黑头怎么去除", "黑头是不是没洗干净", "挤黑头会怎么样",
      "水杨酸去黑头", "长痘能喝牛奶吗", "痤疮护理"],
     ["问牙膏色条谣言（用色条卡）", "问痘坑医美术（就医）"],
     "atomic", "",
     "粉刺黑头=痤疮早期：毛孔皮脂角质堵塞（黑头=油脂氧化非脏）；护理=温和清洁+水杨酸/阿达帕林夜间建立耐受+防晒+少高糖奶；别用手挤撕拉（炎症痘坑）——中重度看皮肤科早干预痘坑。"),
    ("kp_card_hairlosscare",
     "脱发的类型与应对",
     "生活常识知识点内容（人话接口）", "生活常识",
     "掉发多≠脱发：日掉 50-100 根正常。**主要类型**：①**雄激素性脱发**（最"
     "常见，占男性脱发 90%+）——遗传+二氢睾酮（DHT）使毛囊萎缩：男性发际线"
     "后移+头顶稀疏（「M+O」型），女性弥漫性头顶稀疏；**有效治疗**=米诺地尔"
     "（外用促血流，男女可用）+非那雄胺（口服阻 DHT，男性用）——**越早干预越"
     "好**，已坏死的毛囊救不回；②**休止期脱发**——大病/产后/节食/重压后 2-"
     "3 个月弥漫掉发，去除诱因后多可自行恢复；③**斑秃**——免疫异常圆形斑块"
     "状脱落（可就医干预）。**误区**：防脱洗发水只辅助、生姜擦头无证据刺激毛"
     "囊反可能致敏；肾虚≠脱发主因。就医挂皮肤科。",
     ["脱发了怎么办", "脱发是什么原因", "雄激素性脱发",
      "米诺地尔有效吗", "产后脱发能恢复吗", "斑秃"],
     ["问洗头频率（用洗头卡）", "问植发（就医评估）"],
     "atomic", "",
     "掉发多≠脱发（日 50-100 正常）：雄激素性脱发最常见=遗传+DHT 毛囊萎缩（米诺地尔+非那雄胺越早越好）；休止期脱发=产后/大病/节食后弥漫掉去除诱因多恢复；斑秃=免疫斑块状；防脱洗发水辅助生姜无证据——皮肤科就医。"),
]

QUESTIONS = [
    ("QB-822", "粉刺和黑头是怎么形成的？为什么不建议用手挤黑头？", "生活常识", "技术直答",
     ["痤疮", "毛孔", "氧化", "水杨酸", "痘坑", "挤"], "通识拓展197"),
    ("QB-823", "脱发有哪些常见类型？为什么说雄激素性脱发要越早干预越好？", "生活常识", "技术直答",
     ["雄激素性脱发", "米诺地尔", "非那雄胺", "休止期", "斑秃", "皮肤科"],
     "通识拓展197"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"DHT"}
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{4,}", content):
            if word not in whitelist:
                problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


def patch_triggers() -> None:
    """短触发复测缺口：fishbone/ulcer 卡生效条件补口语短触发变体。"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    patches = {
        "kp_card_fishbone": ["鱼刺卡了怎么办", "卡了鱼刺"],
        "kp_card_ulcer": ["嘴破怎么好得快", "嘴巴长溃疡"],
    }
    for nid, extra in patches.items():
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if not row or not isinstance(row[0], str):
            continue
        sa = json.loads(row[0])
        if "comment" in sa and "生效条件" in sa["comment"]:
            old = sa["comment"]["生效条件"]
            for t in extra:
                if t not in old:
                    old = old + [t]
            sa["comment"]["生效条件"] = old
            cur.execute("UPDATE nodes SET state_attributes=? WHERE id=?",
                        (json.dumps(sa, ensure_ascii=False), nid))
            print(f"触发词补强: {nid} -> +{extra}")
    conn.commit()
    conn.close()


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
                               "level:L2", "status:verified", "batch:通识拓展197"],
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
    bank["version"] = "v4.70"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
    patch_triggers()
    print("触发词补强完成")
