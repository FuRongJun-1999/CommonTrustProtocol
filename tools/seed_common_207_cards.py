# -*- coding: utf-8 -*-
"""seed_common_207_cards.py · 通识拓展批次207知识卡+题库（幂等·两卡精批次）

207：生活常识-痛经的科学缓解/生活常识-嘴唇干裂的护理
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
    ("kp_card_dysmenorrhea",
     "痛经的科学缓解",
     "生活常识知识点内容（人话接口）", "生活常识",
     "原发性痛经=子宫内膜释放**前列腺素**引起子宫平滑肌过度收缩+局部缺血疼"
     "痛——**不是「体寒」「着凉」**这种单一原因。**有效缓解**：①**热敷下腹**"
     "（热敷袋/暖宝宝，放松肌肉+改善局部血流，研究证实有效）；②**布洛芬等解"
     "热镇痛药**——抑制前列腺素合成，**疼痛刚开始就吃**效果最好（偶发痛经按"
     "说明服用不伤身、不成瘾——「止痛药依赖」是误解）；③适度运动/充足睡眠"
     "长期可减轻；④红糖水=热水+糖的安慰效应（热量带来舒缓，红糖本身无特殊"
     "功效）。**就医线**：疼痛逐年加重、止痛药无效、经量剧变/非经期也痛——"
     "排查**子宫内膜异位症**等继发性痛经（越拖越重的痛经要查因）。",
     ["痛经怎么缓解", "痛经吃布洛芬有用吗", "痛经能吃止痛药吗",
      "红糖水治痛经是真的吗", "原发性痛经", "痛经越来越重要检查"],
     ["问子宫内膜异位症（就医）", "问月经周期知识"],
     "atomic", "",
     "原发性痛经=前列腺素致子宫过度收缩缺血（非单一体寒）；缓解=热敷下腹+布洛芬早期吃（偶发服用不伤身不成瘾是误解）+红糖水=热水安慰效应；逐年加重/止痛无效→排查子宫内膜异位症等继发痛经。"),
    ("kp_card_chappedlips",
     "嘴唇干裂的护理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "嘴唇**没有皮脂腺、角质层极薄**——最不「抗干」的皮肤。**越舔越干**：舔"
     "唇带来的唾液蒸发时会**带走更多水分**，唾液中的消化酶还刺激唇缘（舔出红"
     "圈）。**正确护理**：①**润唇膏**——选含凡士林/神经酰胺/蜂蜡的基础款"
     "（含香精薄荷的清凉感只是刺激），干裂时**睡前厚涂**当「唇膜」；②多喝"
     "水+室内加湿；③死皮**勿用手撕**（撕出血感染），可热敷软化后轻轻擦；④"
     "**反复开裂结痂不愈**（剥脱性唇炎）或伴嘴角裂口感染（口角炎——常与维生"
     "素 B2 缺乏/真菌相关）→就医。",
     ["嘴唇干裂怎么办", "为什么舔嘴唇更干", "润唇膏怎么选",
      "嘴唇死皮能撕吗", "口角炎是缺什么"],
     ["问皮肤干燥（用干燥卡）", "问口角炎治疗（就医）"],
     "atomic", "",
     "嘴唇无皮脂腺角质薄最易干裂：舔唇=越舔越干（唾液蒸发带水+消化酶刺激）；护理=基础款润唇膏（凡士林/神经酰胺）睡前厚涂+多喝水+死皮勿撕；反复开裂不愈=剥脱性唇炎或口角炎（B2 缺乏）就医。"),
]

QUESTIONS = [
    ("QB-839", "痛经的科学缓解方法有哪些？布洛芬治疗痛经会成瘾吗？", "生活常识", "技术直答",
     ["前列腺素", "热敷", "布洛芬", "早期", "成瘾", "误解"], "通识拓展207"),
    ("QB-840", "嘴唇干裂为什么越舔越干？正确的护理方法是什么？", "生活常识", "技术直答",
     ["唾液", "蒸发", "润唇膏", "凡士林", "死皮", "口角炎"], "通识拓展207"),
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
                               "level:L2", "status:verified", "batch:通识拓展207"],
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
    bank["version"] = "v4.79"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
