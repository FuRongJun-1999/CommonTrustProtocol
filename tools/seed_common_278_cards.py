# -*- coding: utf-8 -*-
"""seed_common_278_cards.py · 通识拓展批次278知识卡+题库（幂等）

278：光学-放大镜的凸透镜原理/光学-老花眼与近视眼的光学区别
KCCS 四要素+题干原句触发词。预检已过（QB-1054/1055+双id可用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_magnifier",
     "放大镜的凸透镜原理",
     "光学通识知识点内容（人话接口）", "基础科学",
     "放大镜为什么能放大：①**凸透镜成像**——物体放在凸透镜一倍焦距以内，"
     "看到的是**正立放大的虚像**（物距小于焦距是放大镜工作条件）；②**怎么"
     "用**——镜片贴近眼睛、物体在焦距内微调距离到最清楚，距离越近放大越"
     "有效但视野越小；③**倍数与曲率**——镜面越凸（曲率大）焦距越短放大"
     "倍数越高，但镜片太厚像差明显边缘发虚；④**成像规律口诀**——一倍焦距"
     "分大小（u<f 放大虚像，u>f 成实像）、二倍焦距分虚实；⑤**同类应用**——"
     "老花镜（凸透镜补看近能力）、显微镜目镜物镜组合、投影仪（f<u<2f 倒立"
     "放大实像）；⑥**冷知识**——放大镜聚光烧纸是在焦点处把大面积阳光"
     "能量集中到小点（能量密度剧增），切勿对人眼。",
     ["放大镜是什么原理", "凸透镜成像规律", "放大镜怎么用倍数最高",
      "一倍焦距分大小", "虚像实像区别", "凸透镜聚焦"],
     ["问像差校正", "问望远镜光路"],
     "atomic", "",
     "放大镜=凸透镜u<f成正立放大虚像+贴近眼焦距内微调+曲率大焦距短倍数高"
     "但像差明显+一倍焦距分大小二倍焦距分虚实+同类老花镜显微镜投影仪+"
     "聚焦烧纸=能量集中勿对人眼。"),
    ("kp_card_presbyopia",
     "老花眼与近视眼的光学区别",
     "生活常识知识点内容（人话接口）", "生活常识",
     "老花与近视别混为一谈：①**成因不同**——近视=眼轴过长或晶状体屈光过"
     "强，远处平行光聚焦在**视网膜前**（看远糊看近清）；老花=睫状肌弹性与"
     "晶状体随年龄退化（约 45 岁起），**看近时调焦能力不足**（看近糊看远"
     "清）——一个是「聚焦太前」，一个是「调焦变弱」，可以同时存在；②**"
     "矫正相反**——近视戴凹透镜（发散光线后移焦点），老花戴凸透镜（聚光"
     "提前，帮助看近）；③**老花镜不能随便买**——每人调节力与瞳距不同，"
     "成品老花镜度数瞳距通用化，长期戴错易视疲劳头晕，应验光配镜；④**"
     "近视的人也会老花**——原来近视者老花后看近可摘近视镜（近视「抵消」"
     "部分老花度数），但看远仍需近视镜；⑤**散光**——角膜不规则散光像差"
     "（远近都糊重影），需柱镜矫正，与老花近视机理不同。",
     ["老花眼和近视眼有什么区别", "老花眼是怎么形成的",
      "近视戴凹透镜还是凸透镜", "老花镜能随便买吗",
      "近视的人会老花吗", "散光是什么"],
     ["问渐进多焦点镜片", "问白内障"],
     "atomic", "",
     "老花vs近视=近视眼轴长焦点在视网膜前(远糊近清)凹透镜矫正+老花晶状体"
     "调焦退化约45岁起(近糊远清)凸透镜矫正+可同时存在+老花镜应验光配镜勿"
     "随便买+近视者老花看近可摘镜部分抵消+散光角膜像差另回事。"),
]

QUESTIONS = [
    ("QB-1054", "放大镜是什么原理？怎么用放大倍数最高？", "基础科学", "技术直答",
     ["凸透镜", "焦距", "虚像", "放大"], "通识拓展278"),
    ("QB-1055", "老花眼和近视眼有什么区别？近视的人也会老花吗？", "生活常识", "技术直答",
     ["眼轴", "调焦", "凹透镜", "凸透镜"], "通识拓展278"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展278"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.49"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
