# -*- coding: utf-8 -*-
"""seed_common_116_cards.py · 通识拓展批次116知识卡+题库（幂等）

116：物理学-磁场对电流的作用/化学-吸烟的危害/生物学-植树造林与碳中和
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_ampereforce",
     "磁场对通电导线的作用（安培力）",
     "基础科学知识点内容（人话接口）", "物理学",
     "磁场对通电导线有力的作用（安培力）——电动机的工作原理：通电导线在磁场中"
     "受力运动，力的方向与**电流方向**和**磁场方向**都有关（左手定则判断：磁感"
     "线穿掌心、四指指电流、拇指指受力方向）。影响安培力大小的因素：电流越大、"
     "磁场越强、导线越长，力越大。能量转化：电能→机械能。与电磁感应对比：电动"
     "机=电生动力（磁场对电流作用），发电机=动生电（电磁感应）——一对「逆运"
     "算」。应用：电动机（家电/电动车/工业电机）、磁悬浮列车（磁力悬浮+直线电"
     "机推进）、扬声器（通电线圈在磁场中振动发声）。",
     ["磁场对通电导线的作用力叫什么", "安培力的方向怎么判断", "电动机的原理",
      "左手定则怎么用", "影响安培力大小的因素", "扬声器的工作原理"],
     ["问电动机换向器", "问磁悬浮原理复习"],
     "atomic", "",
     "安培力=磁场对通电导线的作用力(电动机原理·电能→机械能)：方向=左手定则(磁场穿掌心·四指电流·拇指力)·与电流磁场方向都有关；大小∝电流×磁场×长度。"),
    ("kp_card_smokingharm",
     "吸烟的危害",
     "生活常识知识点内容（人话接口）", "化学",
     "烟草烟雾含数千种化学物质，其中有害的主要有：①**尼古丁**——成瘾元凶（刺"
     "激大脑奖赏系统），并升高血压心率；②**焦油**——黏附呼吸道，含多种致癌物"
     "（肺癌首因，吸烟者肺癌风险为不吸烟者的 10-20 倍）；③**一氧化碳**——与血"
     "红蛋白结合降低携氧能力（缺氧）。二手烟同样有害（不吸烟者被动吸入——儿童"
     "哮喘/肺炎风险增高）。吸烟还增加心脑血管病/慢阻肺/胃溃疡风险。戒烟收益："
     "戒 20 分钟血压恢复、1 年冠心病风险减半、10 年肺癌风险减半——任何时候戒都"
     "不晚。电子烟也含尼古丁且长期安全数据不足——不是戒烟「安全替代品」。",
     ["吸烟的危害有哪些", "香烟烟雾中的有害物质", "尼古丁的作用",
      "二手烟的危害", "戒烟后身体的变化", "电子烟能戒烟吗"],
     ["问肺癌流行病学", "问戒烟方法与药物"],
     "atomic", "",
     "烟害三剑客=尼古丁(成瘾·升压)+焦油(致癌·肺癌 10-20 倍风险)+CO(缺氧)；二手烟同样害人；戒烟 20 分钟血压回·1 年冠心病减半·10 年肺癌减半；电子烟非安全替代。"),
    ("kp_card_treeplant",
     "植树造林与碳中和",
     "基础科学知识点内容（人话接口）", "生物学",
     "树木通过**光合作用**吸收二氧化碳、固定碳元素（储存在木材和土壤中）——植"
     "树造林是「基于自然的碳中和方案」：一棵成年树每年可吸收约 20 公斤 CO₂；森"
     "林是陆地最大的碳储库之一。中国的生态工程：三北防护林（防风固沙）、退耕还"
     "林、天然林保护工程——中国森林覆盖率从新中国成立初约 8.6% 提高到 24%+，"
     "对全球绿化贡献世界第一（NASA 卫星数据）。塞罕坝：三代人 60 年把荒漠变成百"
     "万亩林海（获联合国「地球卫士奖」）。碳汇概念：森林吸收并储存 CO₂ 的能力"
     "——可通过「碳汇交易」变现。但植树不能替代减排：森林固碳速度远赶不上化石"
     "燃料排放速度——**减排+增汇**双管齐下。",
     ["植树造林对碳中和的作用", "一棵树能吸收多少二氧化碳", "塞罕坝精神",
      "什么是碳汇", "中国森林覆盖率", "三北防护林工程"],
     ["问碳汇交易市场", "问树种固碳能力差异"],
     "atomic", "",
     "树=光合固碳(成年树年吸约 20kg CO₂)：塞罕坝三代人造百万亩林(地球卫士奖)；中国森林覆盖率 8.6%→24%+ 全球绿化第一；但森林固碳远慢于化石排放——减排+增汇双管。"),
]

QUESTIONS = [
    ("QB-602", "磁场对通电导线的作用力叫什么", "物理学", "技术直答",
     ["安培力"], "通识拓展116"),
    ("QB-603", "吸烟的危害有哪些", "化学", "技术直答",
     ["尼古丁", "焦油", "一氧化碳"], "通识拓展116"),
    ("QB-604", "植树造林对碳中和的作用", "生物学", "技术直答",
     ["光合", "固碳"], "通识拓展116"),
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
                               "level:L2", "status:verified", "batch:通识拓展116"],
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
    bank["version"] = "v3.0"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
