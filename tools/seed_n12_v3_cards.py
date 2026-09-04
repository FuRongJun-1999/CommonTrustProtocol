# -*- coding: utf-8 -*-
"""seed_n12_v3_cards.py · 知识域拓展第四批知识卡（幂等）

夜批N12：心理学-遗忘曲线/生物学-呼吸作用/化学-元素周期表/物理-杠杆 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_forgettingcurve",
     "遗忘曲线",
     "基础科学知识点内容（人话接口）", "心理学",
     "遗忘曲线（艾宾浩斯 1885 年实验发现）：学习后的遗忘先快后慢——新学内容在"
     "最初 20 分钟遗忘约 40%，1 天后遗忘约 70%，之后遗忘速度大幅放缓。应对方法"
     "是「间隔重复」：在快遗忘的时间点（如 1 天、3 天、7 天、15 天后）复习，"
     "每次复习都会把遗忘曲线「拉平」一些，最终形成长期记忆。死记硬背一次不如"
     "科学地分几次复习。",
     ["什么是遗忘曲线", "遗忘曲线", "艾宾浩斯遗忘曲线", "怎么复习最有效",
      "遗忘的规律是什么", "间隔重复"],
     ["问记忆宫殿法", "问睡眠与记忆"],
     "atomic", "",
     "遗忘曲线 = 先快后慢（20 分钟遗忘 40%）；对抗方法是间隔重复——每次复习拉平曲线。"),
    ("kp_card_respiration",
     "呼吸作用",
     "基础科学知识点内容（人话接口）", "生物学",
     "呼吸作用（细胞呼吸）：生物细胞内把有机物（葡萄糖）氧化分解、释放能量的"
     "过程——与光合作用正好相反。有氧呼吸公式：葡萄糖 + 氧气 → 二氧化碳 + 水 "
     "+ 大量能量（ATP），场所主要在线粒体；无氧呼吸不彻底分解（如肌肉缺氧时产"
     "乳酸、酵母菌产酒精）。呼吸作用是所有活细胞全天候进行的能量供应过程。",
     ["什么是呼吸作用", "呼吸作用", "有氧呼吸和无氧呼吸", "呼吸作用的场所",
      "细胞怎么获得能量", "呼吸作用公式"],
     ["问光合作用", "问发酵"],
     "atomic", "",
     "呼吸作用 = 细胞分解有机物释放能量（ATP）；有氧在线粒体、无氧产乳酸或酒精。"),
    ("kp_card_periodictable",
     "元素周期表",
     "基础科学知识点内容（人话接口）", "化学",
     "元素周期表（门捷列夫 1869 年发现规律）：把元素按原子序数（质子数）递增"
     "排列，性质相似的元素排在同一列（族）——周期性规律让门捷列夫成功预言了"
     "当时未发现的元素（如镓、锗）。表分 7 行（周期）18 列（族）：左边金属、"
     "右边非金属、中间过渡金属；同族元素化学性质相似（如碱金属都活泼）。",
     ["元素周期表", "元素周期表是谁发明的", "门捷列夫", "元素周期表的规律",
      "元素怎么排列", "什么是族和周期"],
     ["问放射性元素", "问稀土元素"],
     "atomic", "",
     "周期表 = 按原子序数排列、同族性质相似；门捷列夫据此预言未发现元素（镓锗）。"),
    ("kp_card_lever",
     "杠杆原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "杠杆原理（阿基米德）：杠杆平衡时，动力×动力臂 = 阻力×阻力臂（F₁L₁ = "
     "F₂L₂）——力臂是支点到力作用线的垂直距离。省力杠杆（动力臂长，如撬棍、"
     "开瓶器）省力但费距离；费力杠杆（动力臂短，如镊子、钓鱼竿）费力但省距离。"
     "「给我一个支点，我能撬动地球」说的就是杠杆的力量。",
     ["什么是杠杆原理", "杠杆原理", "阿基米德杠杆", "省力杠杆",
      "动力臂阻力臂", "撬棍为什么省力"],
     ["问滑轮组", "问斜面原理"],
     "atomic", "",
     "杠杆原理 = 动力×动力臂 = 阻力×阻力臂；动力臂长省力费距离（撬棍/开瓶器）。"),
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
                "name": f"{name}（{dgroup}·基础科学知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——基础科学高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:同域深化第五批"],
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
