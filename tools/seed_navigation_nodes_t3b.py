# -*- coding: utf-8 -*-
"""seed_navigation_nodes_t3b.py · 复合节点第三批（学习方法/沟通表达，幂等）"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_nav_xx_root",
     "学习方法",
     "学习方法知识点内容（人话接口）", "学习",
     "学习方法的底层是记忆规律与主动输出：被动重读效果最差，检索式练习"
     "（合上书回忆）与间隔重复效果最好。",
     ["学习方法不对", "怎么学更高效", "学完就忘"],
     ["问具体课程推荐", "问考试答案"],
     "composite", "学习场景",
     ""),
    ("kp_nav_xx_jy",
     "记忆方法",
     "学习方法知识点内容（人话接口）", "学习",
     "记忆方法核心是检索式练习与间隔重复：合上书主动回忆比重读有效得多；"
     "按遗忘曲线间隔复习（1 天/3 天/7 天）比集中突击保持更久。",
     ["学习场景下怎么记忆", "背了就忘怎么办", "问间隔重复"],
     ["问记忆术表演", "问药物增强记忆"],
     "atomic", "",
     "记忆 = 检索式练习 + 间隔重复：合上书回忆、按 1/3/7 天间隔复习——"
     "重读是最弱的记忆方式。"),
    ("kp_nav_xx_bs",
     "笔记方法",
     "学习方法知识点内容（人话接口）", "学习",
     "笔记的核心不是抄而是加工：用自己的话重写（费曼式），只记不理解的与"
     "结构性的内容；课后整理比课上照抄效果好。",
     ["学习场景下怎么做笔记", "笔记记了不看", "问康奈尔笔记"],
     ["问笔记软件选型", "问手写还是平板"],
     "atomic", "",
     "笔记 = 自己的话重写 + 只记不懂的和结构 + 课后整理——抄写是最低效"
     "的笔记方式。"),

    ("kp_nav_gt_root",
     "沟通表达",
     "沟通知识点内容（人话接口）", "职场",
     "沟通表达的核心是先想清楚听的人需要什么：结构清晰（先结论后细节）、"
     "换位（用对方的语言）、确认（复述对方的意思再回应）。",
     ["沟通表达能力差", "说话没重点", "怎么提高表达能力"],
     ["问主持培训", "问外语口语"],
     "composite", "表达场景",
     ""),
    ("kp_nav_gt_dr",
     "当众发言",
     "沟通知识点内容（人话接口）", "职场",
     "当众发言的紧张来自聚焦自己而非内容：准备结构（观点+两三个论据）、"
     "提前练第一句、把注意力放在「给听众价值」上——练习次数是唯一可靠"
     "的脱敏方式。",
     ["表达场景下当众发言紧张", "开会发言发抖", "问上台讲话技巧"],
     ["问主持人台词", "问演讲稿代写"],
     "atomic", "",
     "当众发言：结构准备好 + 练第一句 + 注意力放内容上——紧张靠次数脱敏，"
     "不靠心理暗示。"),
    ("kp_nav_gt_qt",
     "倾听技巧",
     "沟通知识点内容（人话接口）", "职场",
     "倾听技巧：先听完再回应（不抢话）；复述对方的意思确认理解（你的意思"
     "是不是……）；对情绪先共情再讲道理——多数冲突源于感觉没被听见。",
     ["表达场景下怎么倾听", "总是聊不到一起", "对方觉得我没在听"],
     ["问谈判策略", "问心理咨询"],
     "atomic", "",
     "倾听 = 听完再回应 + 复述确认（你的意思是不是……）+ 情绪先共情再"
     "讲道理。"),
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
                "name": f"{name}（{dgroup}·导航种子T3b）",
                "生效条件": conds,
                "子功能": (f"{name}的条件空间导航入口" if ktype == "composite"
                           else f"{name}——原子知识条目"),
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
                               "level:L2", "status:verified", "batch:T3b"],
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
