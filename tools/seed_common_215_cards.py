# -*- coding: utf-8 -*-
"""seed_common_215_cards.py · 通识拓展批次215知识卡+题库（幂等·两卡精批次）

215：趣味天文-月亮为什么会「跟着我走」/趣味物理-镜子为什么左右颠倒
KCCS 四要素+题干原句触发词。三重预检：月亮跟走双库零覆盖；镜子镜像与
QB-749 老卡划界（具体需查）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_moonfollow",
     "月亮为什么会「跟着我走」",
     "基础科学知识点内容（人话接口）", "天文学",
     "「月亮跟着我走」=**视差角度差异**的视觉现象：①走动时，**近处物体**（"
     "树/路灯）与你的视线夹角变化很大——它们明显「后退」；②月亮距离地球约 "
     "**38 万公里**，你走几百米引起的视线角度变化**小到无法察觉**——月亮在你"
     "视野中的位置几乎不动，看起来就像「一直跟着你」；③同理：远处的山、太阳"
     "星星也「跟着走」；坐车时远处山走得慢、近处电线杆飞快后退（「运动视"
     "差」）——近快远慢是判断距离的天然线索。所以不是月亮偏心，是**距离太远"
     "让视差失效**。",
     ["月亮为什么跟着我走", "月亮为什么跟着人", "视差是什么",
      "为什么远处的山走得慢", "运动视差"],
     ["问月相变化", "问星星为什么眨眼（用折射卡）"],
     "atomic", "",
     "月亮跟走=视差角度差异：近物视线夹角变化大明显后退，月亮 38 万公里远走几百米视差小到无法察觉→视觉位置几乎不动像跟着走；同类=远山太阳；近快远慢的运动视差=判断距离的天然线索。"),
    ("kp_card_mirrorflip",
     "镜子为什么「左右颠倒」",
     "基础科学知识点内容（人话接口）", "物理学",
     "镜子「左右颠倒、上下不颠倒」的经典谜题：①**真相**——镜子根本没有「颠"
     "倒左右」，它做的是**前后翻转**（沿镜面法线把像翻转）：你举右手，镜中人"
     "举的是「他自己的右手」（在他的视角里），位置与你举的手在同一侧；②**为"
     "什么感觉左右反了**——因为**你把镜子里的像想象成了转身面对你的另一个人"
     "**：想象中「转身」这个动作把左右交换了——**是想象中的转身颠倒了左右，"
     "不是镜子**；③**验证**：在透明玻璃后面举右手，玻璃前看——左右并不交换"
     "（没有翻转思维）；文字在镜子里反了，是因为**你把纸转过来对着镜子**——"
     "旋转的是纸。类似的：地图上北下南，「颠倒」都是参照系选择问题。",
     ["镜子为什么左右颠倒", "镜子成像原理", "为什么镜子里字是反的",
      "平面镜成像", "镜子左右反转"],
     ["问光的反射", "问对称与手性"],
     "atomic", "",
     "镜子不做左右颠倒而是前后翻转（沿法线把像翻转）：举右手镜中人举「他的右手」同侧；感觉反了=把像想象成转身面对你的人——是想象中的转身交换了左右不是镜子；文字反了因为旋转的是纸。"),
]

QUESTIONS = [
    ("QB-853", "为什么走路时月亮看起来会「一直跟着你」？", "天文学", "技术直答",
     ["距离", "视差", "角度", "38万公里", "近处"], "通识拓展215"),
    ("QB-854", "镜子成像真的是「左右颠倒」吗？为什么镜子里的文字是反的？", "物理学", "技术直答",
     ["前后翻转", "法线", "转身", "想象", "纸转过来了"], "通识拓展215"),
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
                               "level:L2", "status:verified", "batch:通识拓展215"],
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
    bank["version"] = "v4.86"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
