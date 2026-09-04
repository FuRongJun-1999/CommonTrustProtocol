# -*- coding: utf-8 -*-
"""seed_common_07_cards.py · 通识拓展批次知识卡（幂等）

07：物理-电磁感应/化学-催化剂/地理-板块构造/生物-生态平衡
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_induction",
     "电磁感应现象",
     "基础科学知识点内容（人话接口）", "物理学",
     "电磁感应（法拉第 1831 年发现）：闭合电路的一部分导体在磁场中做切割磁感"
     "线运动时，导体中就会产生感应电流——发电机的工作原理。影响感应电流大小的"
     "因素：磁场强弱、切割速度、线圈匝数。生活中应用：水力/火力发电、无线充电"
     "（电磁感应耦合）、变压器（改变交流电压）。",
     ["什么是电磁感应", "电磁感应", "法拉第电磁感应", "发电机的工作原理",
      "感应电流怎么产生", "电磁感应现象"],
     ["问电动机原理", "问变压器细节"],
     "atomic", "",
     "电磁感应 = 磁场中切割磁感线产生电流（法拉第 1831）；发电机/无线充电/变压器的原理。"),
    ("kp_card_catalyst",
     "催化剂",
     "基础科学知识点内容（人话接口）", "化学",
     "催化剂：能改变化学反应速率而自身的质量和化学性质在反应前后不变的物质。"
     "催化剂通过降低反应的活化能来加快（正催化剂）或减慢（负催化剂）反应——"
     "不改变反应的平衡点。典型例子：二氧化锰（MnO₂）加速过氧化氢分解产生氧气；"
     "人体内酶是生物催化剂（高效专一）；汽车尾气催化转化器将有害气体转化为无害"
     "物质。",
     ["什么是催化剂", "催化剂", "催化剂的特点", "催化剂在反应中会不会被消耗",
      "酶是催化剂吗", "二氧化锰的作用"],
     ["问化学平衡", "问反应速率"],
     "atomic", "",
     "催化剂 = 改变化学反应速率而自身前后不变（质量化学性质均不变）；降低活化能加快反应。"),
    ("kp_card_plate",
     "板块构造学说",
     "基础科学知识点内容（人话接口）", "地理学",
     "板块构造学说：地球岩石圈分为六大主要板块（亚欧/太平洋/美洲/非洲/印度洋/"
     "南极洲），板块在软流层上缓慢移动（每年几厘米）。板块交界处是地质活动活跃"
     "带——碰撞挤压形成山脉（喜马拉雅）、张裂形成裂谷和海洋（东非大裂谷/大红"
     "海）、俯冲形成深海沟与火山地震带（环太平洋火山地震带）。全球约 90% 的地"
     "震和 80% 的火山分布在板块交界处。",
     ["什么是板块构造", "板块运动", "六大板块", "为什么有地震和火山",
      "喜马拉雅山怎么形成的", "环太平洋火山地震带"],
     ["问地震预测", "问海底扩张"],
     "atomic", "",
     "板块构造 = 岩石圈分六大板块在软流层上缓慢移动；交界处多地震火山山脉。"),
    ("kp_card_ecobalance",
     "生态平衡",
     "基础科学知识点内容（人话接口）", "生物学",
     "生态平衡：生态系统中各种生物的数量和比例维持相对稳定的状态——通过食物"
     "链的相互制约和负反馈调节实现（如草多→兔多→草减少→兔减少→草恢复）。破"
     "坏生态平衡的因素：外来物种入侵（无天敌疯狂繁殖）、过度捕猎、环境污染、栖"
     "息地破坏。生态系统的自动调节能力有限——超过限度就会崩溃且难以恢复。",
     ["什么是生态平衡", "生态平衡", "破坏生态平衡的因素", "为什么不能随意引入外来物种",
      "生态系统的自动调节", "生态失衡的例子"],
     ["问生物入侵案例", "问环境保护措施"],
     "atomic", "",
     "生态平衡 = 食物链相互制约+负反馈调节维持稳定；自动调节有限，过度破坏难恢复。"),
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
                               "level:L2", "status:verified", "batch:通识拓展07"],
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
