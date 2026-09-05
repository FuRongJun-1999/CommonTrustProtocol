# -*- coding: utf-8 -*-
"""seed_common_224_cards.py · 通识拓展批次224知识卡+题库（幂等·两卡精批次）

224：生活常识-胃胀气的成因与缓解/生活常识-皱纹与胶原蛋白
KCCS 四要素+题干原句触发词。三重预检：胃胀气（soda 卡仅碳酸产气角度划界）
与皱纹胶原蛋白双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_bloating",
     "胃胀气的成因与缓解",
     "生活常识知识点内容（人话接口）", "生活常识",
     "胃胀气两大来源：①**吞入的空气**——吃饭太快、边吃边说话、嚼口香糖、喝碳"
     "酸饮料；②**肠道细菌产气**——部分食物（豆类/洋葱/西兰花/红薯）含难消"
     "化碳水，被肠道细菌分解产气（**乳糖不耐**者喝奶也产气）。**缓解**：饭"
     "后散步促蠕动、顺时针按摩腹部、少量多次进食、少喝碳酸饮料少嚼口香糖；"
     "**排气（放屁）是正常的**——每天 10-20 次属正常范围，憋着反而难受。**就"
     "医线**：胀气持续加重、伴**体重下降/便血/持续腹痛**——排查肠道器质性疾"
     "病（别都归为「消化不好」）。",
     ["胃胀气怎么回事", "胃胀气怎么缓解", "胀气不能吃什么", "豆类胀气",
      "放屁多正常吗"],
     ["问乳糖不耐", "问肠易激综合征（就医）"],
     "atomic", "",
     "胃胀气两来源=吞入空气[吃饭快嚼口香糖碳酸饮料]+肠道细菌分解难消化碳水[豆类洋葱西兰花]产气；缓解=饭后散步+顺时针按摩+少量多次+少碳酸少口香糖；日排气 10-20 次正常；持续加重伴体重下降便血就医排查器质性。"),
    ("kp_card_wrinkle",
     "皱纹与胶原蛋白",
     "生活常识知识点内容（人话接口）", "生活常识",
     "皱纹的成因：①**自然老化**——**胶原蛋白+弹性蛋白**逐年流失（25 岁后每"
     "年约 1%），皮肤失去支撑与回弹；②**光老化（最大外因）**——**紫外线**破"
     "坏胶原纤维（占皮肤外因老化的 80%+——防晒是最有效的抗皱手段，与防晒卡"
     "联动）；③**表情纹**——表情肌反复收缩（鱼尾纹/抬头纹/法令纹）；④**糖"
     "化**——高糖饮食让胶原蛋白交联变脆发黄。**科学抗皱**：防晒第一+保湿+维"
     "A 醇类（刺激胶原再生，需建立耐受）+充足睡眠；**误区**：口服胶原蛋白→"
     "消化分解为氨基酸**不会定向补到脸上**（不如直接补足蛋白质+维C[胶原合成"
     "需要]）；「美容仪逆转皱纹」夸大。",
     ["皱纹是怎么形成的", "胶原蛋白口服有用吗", "抗皱最有效的方法",
      "光老化是什么", "表情纹"],
     ["问防晒（用防晒卡）", "问皮肤干燥（用干燥卡）"],
     "atomic", "",
     "皱纹=胶原弹性蛋白流失+光老化[紫外线占外因 80%防晒第一]+表情纹+糖化；科学抗皱=防晒+保湿+维 A 醇遵医嘱+睡眠；口服胶原蛋白消化成氨基酸不会定向补脸——补蛋白质维C 更实际。"),
]

QUESTIONS = [
    ("QB-872", "胃胀气是怎么产生的？如何缓解胃胀气？", "生活常识", "技术直答",
     ["吞气", "细菌", "产气", "豆类", "散步", "按摩"], "通识拓展224"),
    ("QB-873", "皱纹是怎么形成的？口服胶原蛋白真的能抗皱吗？", "生活常识", "技术直答",
     ["胶原蛋白", "流失", "光老化", "紫外线", "防晒", "消化"], "通识拓展224"),
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
                               "level:L2", "status:verified", "batch:通识拓展224"],
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
    bank["version"] = "v4.95"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
