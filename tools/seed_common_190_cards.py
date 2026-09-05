# -*- coding: utf-8 -*-
"""seed_common_190_cards.py · 通识拓展批次190知识卡+题库（幂等·单卡+缺口修复）

190：心理学-经典条件反射（巴甫洛夫）——修复复测报告登记的压线题 QB-035
（top=3 脆弱路由：老卡 kp_8536150530 匹配弱）。新卡强化触发词并划界
（斯金纳箱=操作性条件反射，盲盒卡已提）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_classicalcond",
     "经典条件反射（巴甫洛夫）",
     "基础科学知识点内容（人话接口）", "心理学",
     "经典条件反射=俄国生理学家**巴甫洛夫**发现的经典学习现象（1900 年代，"
     "诺贝尔奖得主的消化研究副产品）：狗看到食物会分泌唾液（本能），但反复"
     "「**铃声+食物**」配对后，**单给铃声**狗也流口水——**中性刺激（铃声）"
     "与无条件刺激（食物）反复配对，变成条件刺激，引发条件反应**。核心要素："
     "无条件刺激（食物）/中性刺激→条件刺激（铃声）/条件反应（听铃流涎）。**"
     "人类应用与例子**：「望梅止渴」（谈梅生津=经典条件反射）、广告把产品与"
     "美好画面反复配对、看见医院白大褂紧张、听到手机提示音就想看手机——都是"
     "配对习得。**与操作性条件反射的区别**：经典=刺激引发自动反应（被动配"
     "对，巴甫洛夫）；操作性=行为结果塑造行为（主动试错+奖惩，**斯金纳**）"
     "——盲盒机/游戏抽卡的成瘾设计即操作性条件反射的应用。",
     ["什么是经典条件反射", "巴甫洛夫的狗实验", "经典条件反射和操作性条件反射的区别",
      "望梅止渴是什么反射", "条件刺激", "斯金纳的操作性条件反射"],
     ["问盲盒成瘾（用盲盒卡）", "问操作性条件反射的应用"],
     "atomic", "",
     "经典条件反射=巴甫洛夫：中性刺激（铃声）与无条件刺激（食物）反复配对→条件刺激引发条件反应（望梅止渴/广告联想/白大褂紧张）；区别于斯金纳操作性条件反射（结果塑造行为）——配对被动 vs 试错主动。"),
]

QUESTIONS = [
    ("QB-808", "巴甫洛夫的狗实验说明了什么？经典条件反射的核心机制是什么？", "心理学", "技术直答",
     ["巴甫洛夫", "中性刺激", "配对", "条件刺激", "唾液", "铃声"], "通识拓展190"),
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
                               "level:L2", "status:verified", "batch:通识拓展190"],
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
    bank["version"] = "v4.63"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
