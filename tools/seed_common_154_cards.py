# -*- coding: utf-8 -*-
"""seed_common_154_cards.py · 通识拓展批次154知识卡+题库（幂等·两卡精批次）

154：地理学/物理-极光成因/生物学-鬼压床（睡眠瘫痪）
KCCS 四要素+题干原句触发词。三重预检：极光/太阳风双库零覆盖；鬼压床仅在
willowisp 卡结尾一句举例（睡眠科学主题未覆盖）；蜃景已由折射卡覆盖弃选。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_aurora",
     "极光是怎么来的",
     "人文通识知识点内容（人话接口）", "地理学",
     "极光成因四步链：①**太阳风**——太阳持续向外抛出高能带电粒子流（质子电"
     "子）；②**地磁场导引**——地球磁场像盾牌偏转粒子，但把一部分沿磁力线**导"
     "向南北两极**（这就是极光只在极地附近出现的原因——极光带在磁纬 65-75°，"
     "阿拉斯加/北欧挪威瑞典芬兰冰岛/加拿大黄刀镇是最佳观测地）；③**高空碰"
     "撞发光**——粒子撞入 100-500km 高空大气，把氧、氮原子/分子的电子撞到高"
     "能态，电子回跳释放光子；④**颜色由谁决定**——**氧原子发绿光**（最常见，"
     "100-300km）与高空红光（>300km），**氮分子发蓝紫色**。太阳活动约 **11 年"
     "周期**（太阳峰年极光更强更南可及中纬度）；强太阳风暴还会干扰电网/卫星"
     "通信（1859 年「卡林顿事件」曾使电报机自燃）。注意：极光是发光**大气现"
     "象**，发生在高空，不是「神仙点灯」——爱斯基摩传说/中国古籍「烛龙」都"
     "是古人的诗意想象。",
     ["极光是怎么形成的", "为什么极光在两极", "极光为什么是绿色的",
      "太阳风是什么", "极光哪里看最好", "太阳活动周期"],
     ["问臭氧层（紫外线屏障）", "问地磁倒转"],
     "atomic", "",
     "极光=太阳风带电粒子被地磁场导向两极→撞 100-500km 高空氧氮原子发光：氧绿光最常见(100-300km)氮蓝紫；极光带磁纬 65-75°(阿拉斯加/北欧/黄刀镇)；太阳活动 11 年周期峰年更强；卡林顿事件曾令电报自燃。"),
    ("kp_card_sleepparalysis",
     "鬼压床（睡眠瘫痪）",
     "基础科学知识点内容（人话接口）", "生物学",
     "「鬼压床」=**睡眠瘫痪**（sleep paralysis），一种常见的睡眠生理现象（约 "
     "40-50% 的人一生至少经历一次），与鬼神无关。**机制**：REM（快速眼动）睡眠"
     "期大脑会**关闭全身骨骼肌运动**（防止把梦演出来伤到自己——「肌肉弛缓」"
     "保护机制）；若意识在此期间**提前觉醒**而肌肉抑制尚未解除，就会出现：**"
     "意识清醒但身体动弹不得**、胸口沉重感/呼吸费力感（胸廓肌受抑制的主观放"
     "大）、甚至伴随幻觉（房间里有「人」、压迫感、耳鸣——大脑半梦半醒把梦境"
     "元素投射进真实房间）。**解除方法**：恐慌无用，先**动手指/脚趾/眨眼/转"
     "动眼球**等小肌群，几秒到几十秒内身体控制即恢复。**诱因与预防**：熬夜/规"
     "律紊乱、仰卧睡姿、压力焦虑、过度疲劳——规律作息+侧睡+减压即可大幅减少"
     "发作。频繁发作影响生活才需就医（排查发作性睡病等）。",
     ["鬼压床是什么", "睡眠瘫痪怎么解除", "为什么醒不了动不了",
      "鬼压床有危险吗", "梦魇和鬼压床", "REM睡眠"],
     ["问发作性睡病", "问失眠治疗"],
     "atomic", "",
     "鬼压床=睡眠瘫痪：REM 期肌肉弛缓保护机制未随意识觉醒同步解除→清醒但动不了+胸口沉重+半梦幻觉（40-50% 人一生至少一次，无害）；解除=先动手指脚趾眨眼小肌群；诱因=熬夜仰卧压力，规律作息侧睡可防；频发就医排查。"),
]

QUESTIONS = [
    ("QB-719", "极光是怎么形成的？为什么极光主要出现在地球的南北两极附近？", "地理学", "技术直答",
     ["太阳风", "带电粒子", "地磁场", "两极", "氧", "氮", "发光"], "通识拓展154"),
    ("QB-720", "「鬼压床」的科学解释是什么？醒来动弹不得时应该怎么快速解除？", "生物学", "技术直答",
     ["睡眠瘫痪", "REM", "肌肉", "手指", "脚趾", "眨眼"], "通识拓展154"),
]


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
                               "level:L2", "status:verified", "batch:通识拓展154"],
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
    bank["version"] = "v4.27"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
