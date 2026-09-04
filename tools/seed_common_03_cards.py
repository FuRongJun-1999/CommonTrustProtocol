# -*- coding: utf-8 -*-
"""seed_common_03_cards.py · 通识常识批次知识卡（幂等）

03：编程范式/生态系统/大洋与大洲/光学折射定律
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_refraction",
     "光的折射定律",
     "基础科学知识点内容（人话接口）", "光学",
     "光的折射定律（斯涅尔定律）：光从一种介质斜射入另一种介质时传播方向发生偏"
     "折——入射角正弦与折射角正弦之比等于两介质折射率之比（n₁sinθ₁=n₂sinθ₂）。"
     "光从疏介质进入密介质（如空气入水）折向法线，反之外折。筷子斜插入水看似弯"
     "折即折射的日常体现。全反射：光从密介质射向疏介质且入射角超过临界角时全部"
     "反射——光纤通信的原理。",
     ["光的折射定律", "光的折射", "什么是折射", "折射定律公式",
      "筷子在水里为什么看起来弯", "什么是全反射"],
     ["问反射定律", "问透镜成像"],
     "atomic", "",
     "折射定律 n₁sinθ₁=n₂sinθ₂；疏入密折向法线；全反射=光纤通信原理。"),
    ("kp_card_ecosystem",
     "生态系统的组成",
     "基础科学知识点内容（人话接口）", "生物学",
     "生态系统的四大组成：①非生物环境（阳光、水、空气、土壤——能量与物质来"
     "源）；②生产者（绿色植物/藻类，通过光合作用制造有机物）；③消费者（动物，"
     "直接或间接以植物为食，分初级/次级/三级消费者）；④分解者（细菌真菌，将有"
     "机物分解为无机物归还环境）。物质循环与能量流动沿食物链/网逐级传递，能量"
     "逐级递减（约10%-20%传递效率）。",
     ["生态系统的组成", "生态系统有哪些成分", "什么是生产者", "什么是分解者",
      "生态系统的四个组成部分", "食物链和食物网"],
     ["问能量流动", "问生物多样性"],
     "atomic", "",
     "生态系统 = 非生物环境+生产者+消费者+分解者；能量沿食物链逐级递减10%-20%。"),
    ("kp_card_continents",
     "世界七大洲与四大洋",
     "人文通识知识点内容（人话接口）", "地理学",
     "世界七大洲按面积从大到小：亚洲（最大，约4400万km²）、非洲、北美洲、南"
     "美洲、南极洲（唯一无常住人口）、欧洲（与亚洲连为欧亚大陆）、大洋洲（最"
     "小）。四大洋按面积：太平洋（最大最深）、大西洋、印度洋、北冰洋（最小最"
     "浅最冷）。亚洲与欧洲以乌拉尔山脉-乌拉尔河-里海-高加索山脉为界。",
     ["世界七大洲和四大洋", "最大的洲是什么洲", "七大洲四大洋", "最大的洋",
      "最小的洲是哪个洲", "亚洲和欧洲的分界线"],
     ["问板块构造", "问气候带分布"],
     "atomic", "",
     "七大洲按面积=亚非北美南美南极欧大洋；四大洋=太平洋（最大）大西洋印度洋北冰洋（最小）。"),
    ("kp_card_energysave",
     "能量守恒定律",
     "基础科学知识点内容（人话接口）", "物理学",
     "能量守恒定律（热力学第一定律）：能量既不会凭空产生也不会凭空消灭，只能"
     "从一种形式转化为另一种形式或从一个物体转移到另一个物体，总量保持不变。"
     "常见能量形式：动能、势能、热能、电能、化学能、核能等。永动机不可能制成"
     "正是因为违背了能量守恒。转化实例：水力发电（势能→动能→电能）、摩擦生热"
     "（动能→热能）、光合作用（光能→化学能）。",
     ["什么是能量守恒定律", "能量守恒", "能量守恒定律", "永动机为什么不可能",
      "能量的转化", "能量守恒公式"],
     ["问热力学第二定律", "问核能"],
     "atomic", "",
     "能量守恒 = 能量不生不灭只转化转移；永动机不可能因违背此定律；实例=水电/摩擦生热/光合。"),
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
                               "level:L2", "status:verified", "batch:通识拓展03"],
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
