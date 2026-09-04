# -*- coding: utf-8 -*-
"""seed_n13_v3_cards.py · 知识域拓展第六批知识卡（幂等）

夜批N13：物理-浮力/历史-工业革命/地理-地形类型/化学-酸碱盐 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_buoyancy",
     "浮力与阿基米德原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "浮力与阿基米德原理：浸在液体（或气体）中的物体受到向上的浮力，浮力大小"
     "等于物体排开的液体（气体）所受的重力——F浮 = ρ液·g·V排。物体沉浮判据："
     "物体密度大于液体密度则下沉（如铁沉水），小于则上浮（如木块、密度小于水"
     "的钢铁轮船靠空心结构增大排开水的体积）。万吨巨轮能浮是因为整体平均密度"
     "小于水。",
     ["什么是浮力", "浮力", "阿基米德原理", "轮船为什么能浮在水面",
      "浮力大小与什么有关", "铁为什么沉水而轮船不沉"],
     ["问流体压强", "问密度计算"],
     "atomic", "",
     "浮力 = 物体排开液体的重力（F浮=ρ液·g·V排）；整体平均密度小于液体则浮。"),
    ("kp_card_industrialrev",
     "工业革命",
     "人文通识知识点内容（人话接口）", "世界历史",
     "工业革命：18 世纪 60 年代始于英国的生产技术大革命——以珍妮纺纱机（1765）"
     "和瓦特改良蒸汽机（1785 投入使用）为标志，机器生产取代手工劳动。四次浪潮"
     "：第一次蒸汽时代（纺织+煤炭）、第二次电气时代（电力+内燃机）、第三次信息"
     "时代（计算机+互联网）、当下第四次智能化时代（AI+物联网）。工业革命带来"
     "生产力飞跃，也重塑了城市化和阶级结构。",
     ["什么是工业革命", "工业革命", "第一次工业革命的标志", "蒸汽机是谁改良的",
      "工业革命从哪个国家开始", "四次工业科技革命"],
     ["问文艺复兴", "问信息革命细节"],
     "atomic", "",
     "工业革命 = 18 世纪始于英国、蒸汽机为标志的机器生产革命；历经蒸汽→电气→信息→智能四次浪潮。"),
    ("kp_card_landform",
     "五种基本地形类型",
     "基础科学知识点内容（人话接口）", "地理学",
     "陆地五种基本地形：山地（海拔高、起伏大、坡度陡，如喜马拉雅山）、高原"
     "（海拔高、地面开阔平坦，如青藏高原）、平原（海拔低、平坦宽广，适合农业"
     "与城市，如华北平原）、丘陵（海拔较低、起伏和缓）、盆地（四周高中间低，"
     "如四川盆地）。地形由内力（地壳运动）和外力（风化侵蚀堆积）共同塑造。",
     ["五种基本地形", "地形类型有哪些", "山地高原平原丘陵盆地", "平原是怎么形成的",
      "地形是怎么形成的", "问地形"],
     ["问地震成因", "问河流地貌"],
     "atomic", "",
     "五大地形 = 山地/高原/平原/丘陵/盆地；由内力（地壳运动）与外力（风化侵蚀堆积）共同塑造。"),
    ("kp_card_acidbase",
     "酸碱盐",
     "基础科学知识点内容（人话接口）", "化学",
     "酸碱盐：酸=电离出的阳离子全部是氢离子的化合物（如盐酸 HCl、硫酸 H₂SO₄"
     "，有酸味、能使石蕊变红）；碱=电离出的阴离子全部是氢氧根离子的化合物（如"
     "氢氧化钠 NaOH，滑腻感、能使石蕊变蓝）；盐=酸碱中和生成的化合物（金属离子"
     "+酸根，如食盐 NaCl）。酸碱中和生成盐和水（pH 试纸可测酸碱度，7 为中性）。",
     ["什么是酸碱盐", "酸碱盐", "酸和碱的区别", "常见的酸和碱",
      "中和反应是什么", "pH值是什么"],
     ["问有机物", "问氧化还原"],
     "atomic", "",
     "酸（H⁺阳离子）/碱（OH⁻阴离子）/盐（酸根+金属离子）；中和=酸+碱→盐+水；pH 7 为中性。"),
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
                               "level:L2", "status:verified", "batch:拓展第七批"],
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
