# -*- coding: utf-8 -*-
"""seed_n5_v3_cards.py · 夜间候选域清单v0.3第一批知识卡（幂等）

夜批N5：力学/海洋学/宇宙学/有机化学 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_newton1",
     "牛顿第一定律（惯性定律）",
     "基础科学知识点内容（人话接口）", "力学",
     "牛顿第一定律（惯性定律）：一切物体在不受外力作用时，总保持静止状态或匀速"
     "直线运动状态——物体保持原有运动状态的性质叫惯性，质量是惯性大小的唯一量度"
     "（质量越大惯性越大，与速度无关）。力不是维持运动的原因，而是改变运动状态的原因。",
     ["牛顿第一定律是什么", "什么是惯性定律", "牛顿第一定律", "惯性是什么",
      "力和运动的关系", "惯性大小与什么有关"],
     ["问牛顿第二定律", "问动量守恒"],
     "atomic", "",
     "惯性定律 = 不受外力时保持静止或匀速直线运动；质量是惯性唯一量度；力改变运动而非维持运动。"),
    ("kp_card_oceancurrent",
     "洋流的成因与分布规律",
     "基础科学知识点内容（人话接口）", "海洋学",
     "洋流的主要成因：盛行风吹拂海面推动海水大规模流动（风海流，如信风与西风带"
     "驱动的南北赤道暖流与西风漂流），叠加地转偏向力（北右南左）与大陆轮廓约束，"
     "形成各大洋的环流圈——中低纬环流顺时针（北半球），暖流从低纬流向高纬、寒流"
     "反之。寒暖流交汇处多渔场（如纽芬兰），暖流增温增湿、寒流降温减湿。",
     ["洋流是怎么形成的", "什么是洋流", "洋流的分布规律", "寒流暖流",
      "世界大渔场为什么多在寒暖流交汇处", "问洋流", "洋流对气候的影响"],
     ["问潮汐成因", "问海底地形"],
     "atomic", "",
     "洋流 = 盛行风驱动+地转偏向+大陆约束成环流；暖流增温增湿/寒流降温减湿，寒暖交汇多渔场。"),
    ("kp_card_bigbang",
     "大爆炸宇宙论",
     "基础科学知识点内容（人话接口）", "宇宙学",
     "大爆炸宇宙论：宇宙起源于约 138 亿年前的一次极高温高密度状态膨胀——三大"
     "证据支撑：①星系红移（哈勃发现星系远离速度与距离成正比，宇宙在膨胀）；"
     "②宇宙微波背景辐射（大爆炸残余的热辐射，约 2.7K，1964 年发现）；③氢氦"
     "丰度比（轻元素原初丰度与理论计算吻合）。注意：大爆炸不是在空间中某点的"
     "爆炸，而是空间本身在膨胀。",
     ["大爆炸宇宙论", "宇宙是怎么起源的", "什么是大爆炸", "宇宙大爆炸的证据",
      "宇宙微波背景辐射是什么", "哈勃发现宇宙在膨胀", "宇宙有多少岁了"],
     ["问黑洞细节", "问暗物质"],
     "atomic", "",
     "大爆炸 = 约 138 亿年前高温高密度态膨胀；三大证据=星系红移+微波背景辐射 2.7K+氢氦丰度。"),
    ("kp_card_organicchem",
     "有机化合物的特点",
     "基础科学知识点内容（人话接口）", "有机化学",
     "有机化合物的特点：含碳的化合物（除 CO、CO₂、碳酸盐等外）称有机物，其"
     "核心特征是碳原子成链或成环的骨架结构。与无机物相比：种类极多（碳的四键"
     "组合能力，已超千万种）、大多易燃、熔点低、多为非电解质不导电、难溶于水"
     "易溶于有机溶剂、反应慢且副反应多（常需催化剂加热）。最简单的有机物是甲烷 CH₄。",
     ["有机化合物的特点", "什么是有机物", "有机物和无机物的区别", "有机物",
      "有机物为什么种类多", "最简单的有机物是什么"],
     ["问高分子材料", "问化学键类型"],
     "atomic", "",
     "有机物 = 含碳化合物（碳骨架成链成环）；种类极多/易燃/熔点低/非电解质；最简单是甲烷 CH₄。"),
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
                               "level:L2", "status:verified", "batch:夜间v0.3第一批"],
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
