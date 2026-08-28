# -*- coding: utf-8 -*-
"""seed_whitebox_tutorial_cards.py · 白箱教程条件化知识卡（幂等）

白箱自举主线：荣提供的教程《白箱智能是什么？》条件化提取入库——
「系统使用自身的认知机制描述自身」的自举闭环：教程覆盖的问题
（白箱是什么/四态路由/盲区原则/水的沸点示例）应能被 card_route
路由命中直答。执行字段按规范型纪律（精确行为规范含边界）。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_whitebox_def",
     "白箱智能定义",
     "人工智能知识点内容（人话接口）", "计算机",
     "白箱智能是把条件、知识、规则、执行和验证显式组织起来的智能系统："
     "面对问题依次判断——我面对什么问题、在什么条件下成立、有哪些知识"
     "可处理、条件不足怎么办、结果错误改什么。与 LLM 的分工：LLM 提出"
     "假设与候选，白箱判断在当前条件下是否成立。",
     ["问白箱智能是什么", "什么是白箱智能", "白箱和黑箱的区别"],
     ["问白箱实现源码", "问灵枢商业信息"],
     "atomic", "",
     "白箱智能 = 把条件、知识、规则、执行和验证显式组织的智能系统；"
     "LLM 提出候选，白箱判断当前条件下是否成立。"),
    ("kp_card_four_states",
     "四态路由",
     "人工智能知识点内容（人话接口）", "计算机",
     "四态路由是白箱的核心判定：ACCEPT 条件满足有资格执行；REJECT 条件"
     "冲突明确不适用；DEFER 相关但条件不足，继续寻找缺失条件（条件递归）；"
     "BLINDSPOT 无法建立可靠归属，不强行猜测——明确知道不知道比生成"
     "看起来合理但无法验证的答案更重要。",
     ["问四态路由", "ACCEPT REJECT DEFER BLINDSPOT", "白箱四种状态"],
     ["问四态路由的源码实现", "问其他领域的四态"],
     "atomic", "",
     "四态路由：ACCEPT 条件满足执行；REJECT 条件冲突不适用；DEFER 条件"
     "不足继续找缺失条件；BLINDSPOT 无法归属不强行猜测。"),
    ("kp_card_blindspot",
     "盲区原则",
     "人工智能知识点内容（人话接口）", "计算机",
     "盲区原则：当系统无法建立「问题→条件→知识→规则→执行路径」的有效"
     "条件链时，正确行为不是编造答案，而是声明 BLINDSPOT。明确知道"
     "「不知道」，比生成一个看起来合理但无法验证的答案更重要。",
     ["问盲区原则", "系统不知道该怎么办", "BLINDSPOT 是什么"],
     ["问如何减少盲区", "问未知领域探索"],
     "atomic", "",
     "盲区原则：无法建立有效条件链时声明 BLINDSPOT（不知道）——明确知道"
     "不知道比编造合理但无法验证的答案更重要。"),
    ("kp_card_condroute",
     "条件路由与条件递归",
     "人工智能知识点内容（人话接口）", "计算机",
     "条件路由：不找最相似的答案，而寻找满足当前条件的路径——如高海拔→"
     "大气压降低→沸点降低→食物难煮熟，每步都有自己的知识和条件。条件"
     "递归：两个候选能力关键词相似时（信任累积 vs 信任阈值检查），不急着"
     "选，进入 DEFER 比较条件差异，找当前任务真正需要的条件后重新判断。",
     ["问条件路由", "什么是条件递归", "两个能力相似怎么选"],
     ["问语义检索原理", "问向量数据库"],
     "atomic", "",
     "条件路由 = 按条件找路径（不找相似答案）；条件递归 = 候选相似时进入"
     " DEFER 比较条件差异，找到真正需要的条件后重新判断。"),
    ("kp_card_boiling",
     "水的沸点与海拔",
     "物理知识点内容（人话接口）", "物理",
     "水的沸点约为 100°C 的条件是标准大气压附近。条件链：海拔升高 → "
     "大气压降低 → 水的沸点降低 → 烹饪温度下降 → 食物更难煮熟。这是"
     "「知识脱离条件存在就没有意义」的经典示例。",
     ["问水的沸点", "高原烧水为什么难煮熟", "海拔与沸点"],
     ["问高压锅原理细节", "问其他液体沸点"],
     "atomic", "",
     "水的沸点约 100°C 的条件是标准大气压；海拔升高→气压降低→沸点降低→"
     "食物难煮熟。"),
    ("kp_card_error_update",
     "预测误差与条件更新",
     "人工智能知识点内容（人话接口）", "计算机",
     "白箱的学习方式：预测 → 执行 → 发现结果与预测不符 → 检查遗漏条件 →"
     " 形成候选新规则 → 验证 → 通过固化、失败拒绝。错误不是「调参数」，"
     "而是寻找遗漏条件的入口：若原理论 A+B→X 而实际≠X，发现遗漏 C 后"
     " A+B+C→X 即为新结构。",
     ["问白箱怎么学习", "预测误差怎么处理", "白箱如何更新规则"],
     ["问神经网络反向传播", "问强化学习"],
     "atomic", "",
     "预测误差→条件更新：结果与预测不符时检查遗漏条件，验证通过的新条件"
     "即成为理论结构的一部分——错误是找遗漏条件的入口。"),
    ("kp_card_vs_expert",
     "白箱与专家系统区别",
     "人工智能知识点内容（人话接口）", "计算机",
     "白箱继承了专家系统的显式知识/规则/条件/可验证性，但进一步处理："
     "开放式问题如何产生候选知识、知识如何组合、如何发现并递归寻找缺失"
     "条件、如何从错误更新结构、如何判断自己没有能力。白箱是以条件、显式"
     "知识、规则、验证和递归为核心的智能架构探索，不是专家系统重新包装。",
     ["问白箱和专家系统的区别", "白箱是专家系统吗"],
     ["问专家系统历史", "问 MYCIN 系统"],
     "atomic", "",
     "白箱在专家系统基础上增加：候选知识产生、知识组合、缺失条件递归、"
     "错误更新结构、无能力判断——是架构探索不是重新包装。"),
    ("kp_card_llm_division",
     "LLM 与白箱分工",
     "人工智能知识点内容（人话接口）", "计算机",
     "白箱不是消灭 LLM，而是重新安排其位置：未知问题 → LLM 提出候选解释"
     " → 白箱寻找条件与已有知识 → 符合 ACCEPT / 冲突 REJECT / 条件不足"
     " DEFER / 无法判断 BLINDSPOT。LLM 负责「提出可能是什么」，白箱负责"
     "「判断当前条件下是否成立」。",
     ["问 LLM 和白箱的关系", "白箱需要大语言模型吗"],
     ["问 LLM 微调方法", "问 prompt 工程技巧"],
     "atomic", "",
     "LLM 负责提出可能是什么（候选/假设/开放问题），白箱负责判断当前条件"
     "下是否成立——两者互补而非替代。"),
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
                "name": f"{name}（{dgroup}·白箱教程卡）",
                "生效条件": conds,
                "子功能": f"{name}——白箱教程条件化知识条目（自举：系统描述自身）",
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
                               "level:L2", "status:verified", "batch:白箱教程卡"],
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
