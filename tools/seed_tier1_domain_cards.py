# -*- coding: utf-8 -*-
"""seed_tier1_domain_cards.py · 候选域清单第一梯队知识卡（幂等）

批八：光学/气象气候/地质学/声学 四域各一张，KCCS 四要素完整+短触发变体。
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
     "折射定律（斯涅尔定律）：光从一种介质斜射入另一种介质时，入射角正弦与折射角"
     "正弦之比等于两介质折射率之反比（n1·sinθ1 = n2·sinθ2）；光从疏介质进入密介质"
     "折向法线，从密进入疏折离法线，入射角为零时方向不变。",
     ["问折射定律", "光的折射", "问斯涅尔定律", "问折射"],
     ["问光的反射", "问平面镜成像"],
     "atomic", "",
     "折射定律 = n1·sinθ1 = n2·sinθ2：疏入密折向法线，密入疏折离法线，垂直入射不偏折。"),
    ("kp_card_rainbow",
     "彩虹的成因",
     "基础科学知识点内容（人话接口）", "气象气候",
     "彩虹的成因：阳光进入空中的小水滴时先折射一次进入水滴，在水滴内壁反射一次，"
     "再折射一次离开水滴——不同波长的光折射角不同（紫光偏折最大、红光最小），"
     "白光被分散成红橙黄绿蓝靛紫的彩色圆弧，观察者背对太阳才能看到。",
     ["问彩虹怎么形成", "彩虹成因", "为什么有彩虹", "问彩虹",
      "彩虹是怎样形成的", "彩虹怎样形成", "彩虹如何形成", "彩虹是怎么形成的"],
     ["问极光成因", "问海市蜃楼"],
     "atomic", "",
     "彩虹 = 阳光在水滴内「折射-反射-折射」+ 各波长折射角不同产生色散；背对太阳可见。"),
    ("kp_card_quake",
     "震级与烈度的区别",
     "基础科学知识点内容（人话接口）", "地质学",
     "震级与烈度的区别：震级衡量地震本身释放的能量大小，一次地震只有一个震级"
     "（如里氏 7.0）；烈度衡量某一地点的破坏和震动强烈程度，一次地震有多个烈度"
     "——离震中越近烈度越大，还受震源深度、地质条件、建筑质量影响。",
     ["问震级烈度区别", "震级和烈度", "问地震震级", "问烈度"],
     ["问地震预测", "问板块构造"],
     "atomic", "",
     "震级 = 一次地震只一个（能量大小）；烈度 = 各地点不同（破坏程度，越近震中越大）。"),
    ("kp_card_soundspeed",
     "声速与介质的关系",
     "基础科学知识点内容（人话接口）", "声学",
     "声速与介质的关系规律：一般情况下固体中最快、液体次之、气体最慢（常温空气约"
     " 340 m/s、水中约 1500 m/s、钢铁中约 5000 m/s）——介质弹性模量越大、密度配合"
     "得当，声波传播越快；同一介质中温度越高声速越快。",
     ["问声速", "声音传播速度", "声音在固体液体气体哪个快", "问声速介质"],
     ["问超声波应用", "问音调响度"],
     "atomic", "",
     "声速规律 = 固体 > 液体 > 气体（钢 5000 / 水 1500 / 空气 340 m/s），同介质温度越高越快。"),
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
                               "level:L2", "status:verified", "batch:候选域第一梯队"],
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
