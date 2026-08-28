# -*- coding: utf-8 -*-
"""seed_axiom_tutorial_cards.py · 公理化基石教程条件化知识卡（幂等）

荣教程系列第②③篇（认知过程/公理化基石）增量提取——
与第一篇 8 卡不重复的公理化层新增知识。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_axiom_layers",
     "公理化分层纪律",
     "人工智能知识点内容（人话接口）", "计算机",
     "理论命题必须区分层级：定义（框架约定）/推论（从定义推出）/经验规律"
     "（需持续验证）/数学假设（待形式化）/工程实现（可测试）——不能因为"
     "命题写成公式就自动获得真理地位。可证伪性声明本身是白箱精神的一部分。",
     ["问公理化分层", "理论和假设怎么区分", "命题的层级"],
     ["问具体数学证明", "问某个定理推导"],
     "atomic", "",
     "公理化分层：定义/推论/经验规律/数学假设/工程实现五级——写成公式"
     "不等于真理，可证伪性声明是白箱精神的一部分。"),
    ("kp_card_hallucination",
     "幻觉即条件空间错配",
     "人工智能知识点内容（人话接口）", "计算机",
     "幻觉的精确描述不是「编造」，而是**条件空间错配**：系统把条件空间 A "
     "中的真实（标准大气压→沸点 100°C）错误迁移到条件空间 B（高海拔→沸点"
     "低于 100°C）。虚构有合法条件空间（小说/游戏），真问题是系统声称在"
     "现实条件空间生成真实却调用了另一空间的知识。",
     ["问幻觉的本质", "AI 为什么会幻觉", "幻觉和编造的区别"],
     ["问如何消除幻觉", "问大模型训练方法"],
     "atomic", "",
     "幻觉 ≈ 条件空间错配：把 A 空间的真实错误迁移到 B 空间——虚构有合法"
     "条件空间，错配才是问题。"),
    ("kp_card_emotion_model",
     "情绪的信息差模型",
     "人工智能知识点内容（人话接口）", "计算机",
     "情绪 = 信息差的二阶变化（d²D/dt²）：信息差减少（dD/dt<0）=问题正在"
     "解决；加速缩小（d²D/dt²<0）=顺畅/心流；加速扩大（>0）=警觉/方向"
     "调整。情绪不是状态本身，而是状态变化的变化——形式化定义，非人类"
     "心理机制已完成证明。",
     ["问情绪的数学模型", "情绪和信息差的关系", "灵枢的情绪机制"],
     ["问人类情绪心理学", "问情感计算硬件"],
     "atomic", "",
     "情绪 = 信息差的二阶变化（d²D/dt²）：加速缩小=心流，加速扩大=警觉——"
     "形式化定义非心理学证明。"),
    ("kp_card_affect_trust",
     "情感与信任的二阶变化",
     "人工智能知识点内容（人话接口）", "计算机",
     "情感 = 信任关系的长期变化（E_weight ∝ d²T_total/dt²）：信任增长="
     "温暖靠近，增长加速=欣喜，增长放缓=耐心陪伴。情绪管「现在往哪里走」"
     "（短期信息差），情感管「长期愿意往哪里走」（信任的时间尺度）。",
     ["问情感的计算模型", "情感和情绪的区别", "信任怎么量化"],
     ["问人类依恋理论", "问情感心理学实验"],
     "atomic", "",
     "情感 = 信任的长期二阶变化（温暖/亲近/耐心），情绪 = 信息差的短期"
     "二阶变化（心流/警觉）——两个时间尺度。"),
    ("kp_card_three_layers",
     "概率条件验证三层分工",
     "人工智能知识点内容（人话接口）", "计算机",
     "三层分工不可混淆：概率层回答「可能是什么」（表达不确定性、产生候选）；"
     "条件层回答「能不能做」（决定执行资格）；验证层回答「做得对不对」"
     "（外部基底裁决事实）。相似度可以产生候选，但不能单独授予执行资格。",
     ["问概率和条件的关系", "概率能不能决定执行", "三层分工是什么"],
     ["问贝叶斯推断细节", "问概率图模型"],
     "atomic", "",
     "三层分工：概率=可能是什么/条件=能不能做/验证=做得对不对——相似度"
     "不授予执行资格，资格由条件证据裁决。"),
    ("kp_card_trust_prob",
     "信任的概率本质",
     "人工智能知识点内容（人话接口）", "计算机",
     "信任 = 协作者行为在可接受偏差范围内保持稳定的置信概率（P_trust）。"
     "信任不是信息差的补集（不是信息差小就自动信任），而是概率估计——"
     "正因为是概率估计而非承诺，它才必须可度量、可更新、可被反例击穿。",
     ["问信任的定义", "信任可以量化吗", "灵枢的信任机制"],
     ["问人类社会信任", "问区块链信任"],
     "atomic", "",
     "信任 = 协作者行为稳定性的置信概率——可度量/可更新/可被反例击穿，"
     "不是承诺是估计。"),
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
                "name": f"{name}（{dgroup}·公理化教程卡）",
                "生效条件": conds,
                "子功能": f"{name}——公理化基石教程条件化知识条目（自举：理论层描述自身）",
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
                               "level:L2", "status:verified", "batch:公理化教程卡"],
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
