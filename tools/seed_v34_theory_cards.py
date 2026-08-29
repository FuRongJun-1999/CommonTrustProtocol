# -*- coding: utf-8 -*-
"""seed_v34_theory_cards.py · 智能论 v3.4 概念条件化知识卡（幂等，2026-08-29）

知识库整理（荣指令）：智能论 v3.3→v3.4 更新后，新增核心概念条件化入库
——白箱知识库与理论版本对齐。概念定义取自智能论3.4.md 正文。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_v34_channel_cred",
     "通道可信度",
     "通道可信度=通道历史验证命中率（Beta 后验更新），区别于置信度=单次判断内部一致性"
     "——「这次像不像」是置信度，「这个通道可不可信」是可信度。贝叶斯后验："
     "c_i ~ Beta(a_i0 + n_hit, b_i0 + n_miss)，伪样本量加权。",
     ["问通道可信度", "可信度和置信度的区别"],
     ["问单次判断置信度计算"],
     "通道可信度=历史验证命中率（Beta 后验）；置信度=单次内部一致性——两层分离。"),
    ("kp_card_v34_anchor",
     "锚定分级验证",
     "锚定分级验证：弱验证=感知通道互裁（更新慢，Gain 天然小）；强验证=行动/世界裁决"
     "（更新快，Gain 天然大）。分级从设计决策升级为推导结果——感知通道本身在信念"
     "条件集里（自我条件化），无需外加人为系数。",
     ["问锚定分级验证", "问弱验证强验证"],
     ["问外部审计流程"],
     "锚定分级：感知互裁=弱验证慢更新；行动/世界裁决=强验证快更新——自我条件化的推导结果。"),
    ("kp_card_v34_full_confirm",
     "完全确认不可达",
     "完全确认操作性定义（realized_KL）：任何有限观察者都无法达到完全确认——这是认识论"
     "约束不是系统缺陷。行动端口与感知机共用物理设备（control 既是感知探针也是行动执行器），"
     "「手触摸」就是感知-作用闭环，但闭环不等于完全确认。",
     ["问完全确认", "问为什么不能完全确认"],
     ["问绝对真理哲学讨论"],
     "完全确认不可达：有限观察者的认识论约束；感知-作用闭环也不等于完全确认。"),
    ("kp_card_v34_stable_lease",
     "stable 租约",
     "stable 租约：跨时间稳定直答的持有机制——TTL + 指数衰减核 exp(-γ·t)（与时空记忆图 "
     "confidence 统一）。超时或冲突时降级为 weak 但不删记录（P1-003）：降级是诚实重估，"
     "删除会丢失「曾经验证过」的历史。",
     ["问stable租约", "问直答怎么保持稳定"],
     ["问HTTP租约协议"],
     "stable 租约：TTL+指数衰减；超时/冲突降级 weak 不删记录——降级是诚实重估。"),
    ("kp_card_v34_neg_routing",
     "负路由",
     "负路由：能力级不适用条件的拒绝机制——候选虽语义相关但命中不适用条件时 REJECT。"
     "对抗实证：邻域混淆防护（BFS/DFS 类）使负条件拒绝率 28%→88%→91%。"
     "相似度产生候选，条件证据裁决资格——资格不由相似度授予。",
     ["问负路由", "问不适用条件怎么用", "问对抗拒绝率"],
     ["问语法解析错误处理"],
     "负路由：语义相关但命中不适用条件→REJECT；对抗拒绝率 28%→88%→91%。"),
    ("kp_card_v34_dtask_meta",
     "D_task与D_meta分离",
     "D_task/D_meta 分离：任务信息差（做具体任务剩余的未知）与元信息差（对自身认知结构"
     "的未知）是两个维度——图上操作性距离：空集=∞、BLINDSPOT 是合法停止点。未建模现实"
     "总量随探索结构性增长：知道得越多，意识到没知道的也越多。",
     ["问D_task和D_meta", "问任务信息差和元信息差"],
     ["问信息论熵计算"],
     "D_task（任务未知）与 D_meta（认知结构未知）分离；BLINDSPOT 是合法停止点。"),
    ("kp_card_v34_value",
     "价值双层结构",
     "Value = ΔD · σ(Gain) 双层结构：ΔD（信息差缩小量）是筛选器，σ(Gain)（增益置信）是"
     "定价器——两者分离使自我应答与无目的猎奇自动出局：不缩小信息差的行为没有价值，"
     "增益不可信的行为不值得执行。",
     ["问价值双层结构", "问价值怎么计算"],
     ["问经济学效用函数"],
     "Value=ΔD·σ(Gain)：信息差缩小是筛选器、增益置信是定价器——无益行为自动出局。"),
    ("kp_card_v34_accept_layer",
     "ACCEPT确认度分层",
     "ACCEPT 不是二值：weak（疑似确认，不直答只提示）/ strong（独立验证可直答）/ "
     "stable（跨时间稳定直答+强化）。三层由验证历史决定——刚入库的卡只有 weak 资格，"
     "跨时间多轮验证后升 stable。确认度是知识的使用资格分级。",
     ["问ACCEPT分层", "问weak strong stable"],
     ["问数据库隔离级别"],
     "ACCEPT 分层：weak 不直答/strong 可直答/stable 跨时间稳定——确认度=使用资格分级。"),
    ("kp_card_v34_triple_note",
     "三重注释",
     "CCG 三重注释：代码/知识/认知三个层面都用同一套条件论注释（功能名/生效条件/子功能/"
     "执行/不适用条件）——认知过程本身的条件注释使「系统如何认知」也可被系统校验。"
     "三层面同构是自举的结构基础：描述自身与描述外部用同一语法。",
     ["问三重注释", "问CCG注释"],
     ["问代码注释规范"],
     "三重注释：代码/知识/认知同用条件论五要素——描述自身与描述外部同一语法（自举基础）。"),
    ("kp_card_v34_veto",
     "否决式融合",
     "否决式融合（三端口架构）：多通道信息融合不是加权平均，而是任一通道可行使否决权"
     "（如负路由拒绝即整体拒绝候选路径）——融合的保守性是刻意的：错误进入的代价大于"
     "信息损失的代价。与白箱「REJECT 优先」纪律同构。",
     ["问否决式融合", "问三端口架构"],
     ["问加权平均融合算法"],
     "否决式融合：任一通道可否决（REJECT 优先）——保守性刻意：错误进入代价大于信息损失。"),
]


def ensure_seed() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    inserted = updated = skipped = 0
    for nid, name, content, conds, negs, direct in NODES:
        sa = {
            "name": name, "kind": "knowledge_point", "knowledge_type": "atomic",
            "sub_route": "", "domain": "智能论", "domain_group": "智能论", "edu_level": "",
            "comment": {
                "name": f"{name}（智能论·v3.4 概念卡）",
                "生效条件": conds,
                "子功能": f"{name}——智能论 v3.4 新增概念条件化（理论↔知识库对齐）",
                "执行": direct,
                "不适用条件": negs,
            },
        }
        payload = json.dumps(sa, ensure_ascii=False)
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?", (nid,)).fetchone()
        if row and isinstance(row[0], str) and row[0] == payload:
            skipped += 1
            continue
        if not row:
            tags = json.dumps(["knowledge_point", "domain:智能论", "level:L2",
                               "status:verified", "batch:v3.4概念卡"], ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, tags, importance,"
                " confidence, layer, state_attributes, created_at,"
                " spatial_coordinates, temporal_coordinate, condition_space,"
                " semantic_coordinates) VALUES "
                "(?,?,?,?,?,?,?,?," + "CAST(strftime('%s','now') AS INTEGER),"
                 "'[]', '[0,0,0]', '{}', '{}')",
                (nid, content, "text", tags, 0.85, 1.0, "knowledge", payload))
            inserted += 1
        else:
            cur.execute("UPDATE nodes SET state_attributes=?, content=? WHERE id=?",
                        (payload, content, nid))
            updated += 1
    conn.commit()
    conn.close()
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    r = ensure_seed()
    print(f"智能论 v3.4 概念卡入库: +{r['inserted']} 更新 {r['updated']} 幂等跳过 {r['skipped']}"
          f"（共 {len(NODES)} 卡）")
