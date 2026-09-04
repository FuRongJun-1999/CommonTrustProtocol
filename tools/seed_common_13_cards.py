# -*- coding: utf-8 -*-
"""seed_common_13_cards.py · 通识拓展批次知识卡（幂等）

13：经济学-供需关系/心理学-认知偏差/环境科学-碳中和/语言学-文字的起源
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_supplydemand",
     "供需关系",
     "基础科学知识点内容（人话接口）", "经济学",
     "供需关系决定市场价格：需求=消费者愿意且能够购买的商品数量（价格越高需"
     "求越少）；供给=生产者愿意且能够提供的商品数量（价格越高供给越多）；供"
     "求平衡时形成均衡价格。需求变化因素：收入、偏好、替代品价格、互补品价"
     "格。供给变化因素：生产成本、技术进步、政府政策。供需不匹配→短缺（抢购"
     "）或过剩（积压）。",
     ["什么是供需关系", "供需关系", "需求和供给", "价格怎么决定",
      "供需平衡", "为什么有的东西贵有的便宜"],
     ["问通货膨胀", "问垄断"],
     "atomic", "",
     "供需决定价格：需求随价格上升而减少、供给随价格上升而增加；均衡=供需相等点。"),
    ("kp_card_cogbias",
     "常见的认知偏差",
     "基础科学知识点内容（人话接口）", "心理学",
     "常见的认知偏差：确认偏差（只关注支持自己观点的信息，忽略反面证据）；锚"
     "定效应（过度依赖最先获得的信息做判断）；可得性偏差（越容易想起的事越认"
     "为常见——如空难新闻多所以觉得坐飞机危险）；幸存者偏差（只关注成功案例忽"
     "略失败案例——如「读书无用论」源于只看到辍学成功者）；达克效应（能力不足"
     "的人反而高估自己）。",
     ["常见的认知偏差", "什么是确认偏差", "什么是幸存者偏差", "锚定效应",
      "达克效应", "认知偏差有哪些"],
     ["问行为经济学", "问决策树"],
     "atomic", "",
     "认知偏差 = 确认偏差+锚定效应+可得性偏差+幸存者偏差+达克效应——系统性偏离理性判断的思维模式。"),
    ("kp_card_carbonneutral",
     "碳中和",
     "基础科学知识点内容（人话接口）", "环境科学",
     "碳中和：在一定时间内直接或间接产生的二氧化碳排放总量，通过植树造林、节"
     "能减排、碳捕集等方式全部抵消，实现净零排放。中国承诺 2030 年前实现碳达"
     "峰（排放达到峰值后不再增长）、2060 年前实现碳中和。实现路径：能源转型"
     "（煤→风/光/核等清洁能源）、工业减排、交通电动化、碳交易市场（用市场机"
     "制激励减排）。",
     ["什么是碳中和", "碳中和", "碳达峰和碳中和", "怎么实现碳中和",
      "中国碳中和目标", "碳交易是什么"],
     ["问温室效应细节", "问新能源技术"],
     "atomic", "",
     "碳中和 = CO₂排放量=吸收抵消量→净零排放；中国目标2030碳达峰、2060碳中和。"),
    ("kp_card_writingorigin",
     "文字的起源",
     "基础科学知识点内容（人话接口）", "语言学",
     "文字的起源：文字是记录语言的书写符号系统，起源多为图画→象形文字→表意"
     "文字→表音文字的演变。最古老的文字：苏美尔楔形文字（约公元前3200年，两"
     "河流域）、古埃及圣书字（约公元前3100年）、中国甲骨文（约公元前1300年商"
     "代）。甲骨文是中国已知最早的成熟文字系统——1899 年王懿荣首次从中药龙骨"
     "上发现，已出土约15万片、单字约4500个（已释读约1500个）。",
     ["文字的起源", "最早的文字是什么", "甲骨文是谁发现的", "中国最早的文字",
      "楔形文字", "文字是怎么产生的"],
     ["问印刷术", "问方言"],
     "atomic", "",
     "文字起源 = 图画→象形→表意→表音；最古老=苏美尔楔形文字；甲骨文=中国最早成熟文字（商代）。"),
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
                               "level:L2", "status:verified", "batch:通识拓展13"],
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
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
