# -*- coding: utf-8 -*-
"""seed_night1_v2_cards.py · 夜间候选域清单v0.2第一组知识卡（幂等）

夜批N1：热学/电磁学/几何/概率统计 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_heattransfer",
     "热传递三种方式",
     "基础科学知识点内容（人话接口）", "热学",
     "热传递三种方式：传导（热量通过物体直接传递，金属勺放热汤里勺柄变热）、"
     "对流（靠流体流动传热，烧水时水的翻滚、暖气使房间变暖）、辐射（以电磁波形式"
     "传热，不需要介质，太阳的热穿过真空到地球）。三种方式可同时发生。",
     ["热传递有哪几种方式", "热传递三种方式", "什么是热传导", "问对流", "问热辐射",
      "太阳的热怎么传到地球", "热是怎么传播的"],
     ["问热力学定律", "问比热容"],
     "atomic", "",
     "热传递三方式 = 传导（直接传）+ 对流（流体流动传）+ 辐射（电磁波传，可穿真空）。"),
    ("kp_card_ohmlaw",
     "欧姆定律",
     "基础科学知识点内容（人话接口）", "电磁学",
     "欧姆定律：导体中的电流与电压成正比、与电阻成反比，公式 I = U/R——电压"
     "（伏特 V）是推动电流的「压力」，电阻（欧姆 Ω）是阻碍电流的性质，电流"
     "（安培 A）是单位时间通过的电荷量。例如 220V 电压加在 44Ω 电阻上，电流"
     "为 220/44 = 5A。",
     ["什么是欧姆定律", "欧姆定律", "电流电压电阻的关系", "问 I=U/R",
      "欧姆定律公式", "电阻怎么影响电流"],
     ["问电磁感应", "问串并联电路计算"],
     "atomic", "",
     "欧姆定律 I = U/R：电流与电压成正比、与电阻成反比（220V/44Ω = 5A）。"),
    ("kp_card_triangangle",
     "三角形内角和",
     "基础科学知识点内容（人话接口）", "几何",
     "三角形内角和定理：任意平面三角形的三个内角之和恒等于 180°。等边三角形"
     "每个内角 60°；直角三角形两个锐角之和为 90°。证明思路：过一顶点作对边的"
     "平行线，用内错角相等把三个角拼成一个平角。n 边形内角和 = (n-2)×180°。",
     ["三角形内角和是多少", "三角形内角和", "问三角形角度", "内角和定理",
      "n边形内角和", "等边三角形每个角是多少度"],
     ["问圆的性质", "问立体几何"],
     "atomic", "",
     "三角形内角和 = 180°（等边各 60°）；n 边形内角和 = (n-2)×180°。"),
    ("kp_card_probability",
     "概率的基本含义",
     "基础科学知识点内容（人话接口）", "概率统计",
     "概率：描述随机事件发生可能性的数值，范围 0 到 1——0 表示不可能事件，"
     "1 表示必然事件。古典概型计算：概率 = 符合条件的结果数 ÷ 所有等可能结果"
     "总数。例如掷一枚均匀硬币正面朝上概率 1/2；掷两枚都正面 1/4（1/2×1/2，"
     "独立事件概率相乘）。平均数易受极端值影响，中位数不受——收入统计常用中位数。",
     ["什么是概率", "概率怎么算", "概率的取值范围", "掷硬币概率",
      "平均数和中位数的区别", "问独立事件"],
     ["问贝叶斯定理细节", "问方差计算"],
     "atomic", "",
     "概率 ∈ [0,1]，古典概型 = 符合数÷总数；独立事件相乘；中位数不受极端值影响。"),
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
                               "level:L2", "status:verified", "batch:夜间v0.2第一组"],
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
