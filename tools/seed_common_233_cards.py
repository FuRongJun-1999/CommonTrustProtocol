# -*- coding: utf-8 -*-
"""seed_common_233_cards.py · 通识拓展批次233知识卡+题库（幂等·两卡精批次）

233：生活常识-擦伤的正确处理/生活常识-电热毯的安全使用
KCCS 四要素+题干原句触发词。三重预检：擦伤处理与 RICE[扭伤]/烫伤卡划界；
电热毯安全与 jouleheat 卡[原理角度]划界。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_abrasion",
     "擦伤的正确处理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "擦伤（皮肤浅表破损）处理步骤：①**冲洗**——流动清水或生理盐水冲洗伤口"
     "去泥沙异物（最关键一步——脏东西残留=感染源）；②**消毒**——**碘伏**"
     "由伤口中心向外画圈消毒（酒精直接涂伤口剧痛且延迟愈合——碘伏才是伤口"
     "首选）；③**保护**——浅小擦伤可暴露保持干燥自愈；渗液多或易摩擦部位用"
     "**透气敷料/创可贴**覆盖（湿润环境反而愈合更快——「结痂干晾」旧观念已"
     "被湿润愈合理论修正）；④**换药**——敷料浸湿或污染即换，愈合期观察红肿"
     "；⑤**就医线**——伤口深/大/污染重（泥土铁锈）/动物咬伤/面部伤口——就"
     "医清创，必要时**打破伤风**与缝合。",
     ["擦伤怎么处理", "擦伤用什么消毒", "碘伏和酒精的区别",
      "伤口要晾干还是保湿", "擦伤多久能好", "破伤风什么时候要打"],
     ["问烫伤处理（用烫伤卡）", "问破伤风疫苗"],
     "atomic", "",
     "擦伤处理=流动水冲洗去泥沙[最关键]+碘伏由内向外消毒[酒精刺激伤口痛]+透气敷料或暴露+敷料浸湿污染即换；湿润环境愈合更快旧观念已修正；深大污染重动物咬伤就医清创必要时打破伤风。"),
    ("kp_card_electricblanket",
     "电热毯的安全使用",
     "生活常识知识点内容（人话接口）", "生活常识",
     "电热毯安全要点：①**睡前预热、睡前关闭**——通电加热被窝后**关电源再睡"
     "**（整夜通电有低温烫伤+漏电双重风险）；②**勿折叠使用**——折叠处局部"
     "过热易引发故障甚至火灾；③**勿放湿衣物/尿湿风险人群**（婴儿/失禁老人）"
     "慎用（水导电）；④**低温烫伤**——44-51°C 的「温和热源」长时间接触皮肤"
     "也会造成**深部烫伤**（比高温烫伤更深更难愈——因为不知不觉持续受热）；"
     "⑤老人/糖尿病人/孕妇感觉迟钝或需谨慎，优先用**热水袋睡前暖被再取出**；"
     "⑥每年使用前**检查电源线有无破损老化**，超期（约 6 年）更换。",
     ["电热毯能开一整晚吗", "电热毯安全使用", "低温烫伤是什么",
      "电热毯会漏电吗", "电热毯用几年更换"],
     ["问保温杯（同热安全）", "问热水袋使用"],
     "atomic", "",
     "电热毯安全=睡前预热睡前关[勿整夜通电]+勿折叠[局部过热火灾]+低温烫伤风险[44-51°C 长接触也伤]；婴儿失禁老人慎用；每年查电源线老化约 6 年更换；热水袋暖被后取出更稳。"),
]

QUESTIONS = [
    ("QB-891", "擦伤后应该怎么正确处理伤口？为什么消毒用碘伏而不是酒精？", "生活常识", "技术直答",
     ["流动水", "冲洗", "碘伏", "酒精", "敷料", "破伤风"], "通识拓展233"),
    ("QB-892", "电热毯可以整晚通电使用吗？什么是「低温烫伤」？", "生活常识", "技术直答",
     ["整夜", "低温烫伤", "折叠", "漏电", "睡前关闭"], "通识拓展233"),
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
                               "level:L2", "status:verified", "batch:通识拓展233"],
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
    bank["version"] = "v5.04"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
