# -*- coding: utf-8 -*-
"""seed_navigation_nodes_t3.py · T3 复合节点扩充批次（幂等）

《自举任务书_v0.1》T3：按 seed_navigation_nodes 模式，从用户对话高频域
手工规范 + 白箱生成子叶卡（每复合 2 叶起步）。本批 3 复合根 × 2 叶 = 9 节点：
  编程入门（学习阶段） / 失眠调理（症状类型） / 职场汇报（汇报场景）

纪律：手工标注、增量插入、防误标污染路由（不做自动推断）。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

# (id, name, domain, domain_group, content, 生效条件, 不适用条件,
#  knowledge_type, sub_route, 直答)
NODES = [
    # ---- 复合根：编程入门 ----
    ("kp_nav_bc_root",
     "编程入门",
     "计算机科学知识点内容（人话接口）", "计算机",
     "编程入门的路径：先选一门合适语言建立正反馈，再用项目驱动练习——顺序错了容易放弃。",
     ["想学编程", "编程从哪开始", "零基础学编程"],
     ["问具体框架源码", "问算法竞赛技巧"],
     "composite", "学习阶段",
     ""),
    # 叶 1：语言选择
    ("kp_nav_bc_yy",
     "语言选择",
     "计算机科学知识点内容（人话接口）", "计算机",
     "零基础首选 Python：语法接近自然语言、反馈快、生态全——第一门语言的目标是建立信心而非追求性能。",
     ["学习阶段下怎么选语言", "第一门编程语言学哪个", "问 Python 适合入门吗"],
     ["问工资高低对比"],
     "atomic", "",
     "零基础首选 Python——第一门语言的目标是建立信心，语法简单反馈快比性能重要。"),
    # 叶 2：练习方法
    ("kp_nav_blx",
     "练习方法",
     "计算机科学知识点内容（人话接口）", "计算机",
     "学编程靠项目驱动：每学一个语法点就写小程序用起来，卡住先自己查 30 分钟再求助——肌肉记忆来自写不是看。",
     ["学习阶段下怎么练习", "看视频懂了但不会写", "学完就忘怎么办"],
     ["问培训班推荐"],
     "atomic", "",
     "项目驱动练习：学一个语法点写一个小程序，卡住先自己查 30 分钟——会写来自动手不是看视频。"),

    # ---- 复合根：失眠调理 ----
    ("kp_nav_sm_root",
     "失眠调理",
     "医学与健康知识点内容（人话接口）", "健康",
     "失眠调理先分型：入睡困难与夜间易醒的对策不同——共同基底是固定作息与睡前仪式。",
     ["睡不着", "失眠怎么办", "睡眠不好"],
     ["问安眠药处方剂量"],
     "composite", "症状类型",
     ""),
    # 叶 1：入睡困难
    ("kp_nav_sm_rs",
     "入睡困难",
     "医学与健康知识点内容（人话接口）", "健康",
     "入睡困难核心是让大脑降速：睡前 1 小时离开屏幕与工作，卧室只用于睡觉；躺下 20 分钟没睡意就起来做无聊的事再回床。",
     ["症状类型是躺下睡不着", "入睡困难怎么破", "越想睡越清醒"],
     ["问白天嗜睡病因"],
     "atomic", "",
     "躺下 20 分钟没睡意就起床做无聊的事，有困意再回床——床只留给睡觉，大脑才会建立条件反射。"),
    # 叶 2：夜间易醒
    ("kp_nav_sm_yx",
     "夜间易醒",
     "医学与健康知识点内容（人话接口）", "健康",
     "夜间易醒先排查外因：室温、光线、声音、睡前饮酒咖啡因；醒来别看时间别刷手机，用缓慢呼吸等困意自然回来。",
     ["症状类型是半夜醒来", "夜里容易醒怎么办", "早醒睡不着"],
     ["问打呼噜手术"],
     "atomic", "",
     "半夜醒来不看时间不刷手机，缓慢呼吸等困意回来；持续易醒先查睡前饮酒与咖啡因。"),

    # ---- 复合根：职场汇报 ----
    ("kp_nav_zc_root",
     "职场汇报",
     "管理学知识点内容（人话接口）", "职场",
     "职场汇报的关键是结论先行：先给结果与建议，再讲依据与过程——听的人时间有限。",
     ["怎么向领导汇报", "汇报工作紧张", "工作汇报没条理"],
     ["问离职谈判"],
     "composite", "汇报场景",
     ""),
    # 叶 1：结构化表达
    ("kp_nav_zc_jg",
     "结构化表达",
     "管理学知识点内容（人话接口）", "职场",
     "汇报用三段式：结论（做了什么/结果如何）→ 关键依据（数据/事实，不超过 3 点）→ 下一步计划；细节备着等追问。",
     ["汇报场景下怎么组织内容", "汇报抓不住重点", "说了一堆领导没听懂"],
     ["问简历怎么写"],
     "atomic", "",
     "汇报三段式：先结论、再三点关键依据、最后下一步计划——细节备着等追问，不要一上来讲过程。"),
    # 叶 2：向上沟通
    ("kp_nav_zc_xt",
     "向上沟通",
     "管理学知识点内容（人话接口）", "职场",
     "向上沟通对齐的是预期：主动同步进展与风险，坏消息早说并带上应对选项，让领导做选择题不做问答题。",
     ["汇报场景下怎么跟领导沟通", "坏消息不敢说", "领导总临时加需求"],
     ["问同事矛盾调解"],
     "atomic", "",
     "主动同步进展与风险：坏消息早说并带应对选项——让领导做选择题，不做问答题。"),
]


def ensure_schema_and_seed() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    inserted = updated = skipped = 0
    for nid, name, domain, dgroup, content, conds, negs, ktype, sub_route, direct in NODES:
        if not nid or not name:  # 占位条目跳过
            continue
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        # 幂等真判据：期望 payload 与库存完整一致则 skip（首批脚本的
        # fingerprint 键判据永不生效，重跑会刷 created_at——本批修正）
        sa = {
            "name": name,
            "kind": "knowledge_point",
            "knowledge_type": ktype,
            "sub_route": sub_route,
            "domain": domain,
            "domain_group": dgroup,
            "edu_level": "",
            "comment": {
                "name": f"{name}（{dgroup}·导航种子T3）",
                "生效条件": conds,
                "子功能": (f"{name}的条件空间导航入口" if ktype == "composite"
                           else f"{name}——原子知识条目"),
                "执行": direct or content,
                "不适用条件": negs,
            },
        }
        payload = json.dumps(sa, ensure_ascii=False)
        if row and isinstance(row[0], str) and row[0] == payload:
            skipped += 1
            continue
        if not row:
            tags = json.dumps(["knowledge_point", f"domain:{domain}",
                               "level:L2", "status:verified",
                               f"nav:{sub_route or 'root'}", "batch:T3"],
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
    print(json.dumps(ensure_schema_and_seed(), ensure_ascii=False))
