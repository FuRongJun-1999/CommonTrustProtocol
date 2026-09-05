# -*- coding: utf-8 -*-
"""seed_common_232_cards.py · 通识拓展批次232知识卡+题库（幂等·两卡精批次）

232：生活常识-眼睛进异物的处理/生活常识-便秘的成因与缓解
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
    ("kp_card_eyeirritant",
     "眼睛进异物的处理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "眼睛进异物（沙尘/睫毛/小虫）的正确处理：①**勿揉眼**——揉会划伤角膜（"
     "异物如砂纸摩擦）；②**多眨眼**——让泪水自然冲刷异物（泪液冲刷是天然机"
     "制）；③**翻开眼睑找**——用干净水冲洗或轻拉上睑覆盖下睑瞬目，异物多藏"
     "在**上睑睑板沟**或下睑；④**冲不出来**——闭眼用干净水杯盛水浸眼眨动，"
     "或就医由医生取出；⑤**紧急情况**——化学物质（酸/碱）入眼：**立即用大"
     "量清水持续冲洗 15 分钟以上**再就医（冲洗比送医更急）；⑥**异物嵌入眼球"
     "**（如高速飞溅的铁屑）——**勿自行取出**，用干净杯罩住立即就医。",
     ["眼睛进异物怎么办", "眼睛进沙子怎么处理", "眼睛进东西不能揉",
      "化学物质入眼怎么冲洗", "隐形眼镜在眼睛里取不出来"],
     ["问角膜炎（就医）", "问干眼（用干眼卡）"],
     "atomic", "",
     "眼进异物=勿揉[划伤角膜]+多眨眼促泪冲+翻开眼睑找湿棉签蘸取+冲不出就医；化学入眼=立即大量清水持续冲洗 15 分钟以上再就医[冲洗比送医更急]；嵌入眼球勿自取杯罩就医；隐形眼镜干眼勿强取先润再取。"),
    ("kp_card_constipation",
     "便秘的成因与缓解",
     "生活常识知识点内容（人话接口）", "生活常识",
     "便秘=排便次数减少（每周少于 3 次）+粪便干硬+排便困难：①**成因**——膳"
     "食纤维少、饮水不足、久坐少动、憋便习惯（忽视便意直肠感受器迟钝）、部分"
     "药物（钙剂/铁剂/某些抗抑郁药）；②**缓解**——**膳食纤维 25-30g/天**（"
     "全谷/蔬果/豆类）+**足量饮水 1.5-2L**（纤维没水反加重）+规律运动+**定"
     "时排便**（早餐后胃结肠反射最强时蹲 5-10 分钟培养习惯，勿带手机久蹲）"
     "；③**泻药勿长期用**——刺激性泻药（番泻叶/大黄）长期用致结肠黑变病+依"
     "赖；④**就医线**——便血、大便变细、体重下降、突然便秘腹泻交替（排查肠"
     "道器质性疾病）。",
     ["便秘怎么办", "便秘吃什么最快排便", "便秘的原因", "膳食纤维",
      "长期用泻药的危害", "定时排便习惯"],
     ["问肠镜检查（就医）", "问益生菌（用乳酸菌卡）"],
     "atomic", "",
     "便秘=每周<3 次+干硬难排：成因=纤维少水少久坐憋便；缓解=纤维 25-30g/天+饮水 1.5-2L+运动+早餐后定时蹲 5-10 分钟培养习惯；刺激性泻药长期用=结肠黑变病依赖；就医线=便血变细体重下降便秘腹泻交替。"),
]

QUESTIONS = [
    ("QB-889", "眼睛进异物应该怎么正确处理？为什么不能用手揉眼睛？", "生活常识", "技术直答",
     ["揉", "角膜", "眨眼", "冲洗", "化学", "15分钟"], "通识拓展232"),
    ("QB-890", "便秘的成因有哪些？为什么不能长期依赖刺激性泻药？", "生活常识", "技术直答",
     ["纤维", "饮水", "久坐", "泻药", "结肠黑变", "依赖"], "通识拓展232"),
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
                               "level:L2", "status:verified", "batch:通识拓展232"],
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
    bank["version"] = "v5.03"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
