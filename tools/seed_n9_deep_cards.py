# -*- coding: utf-8 -*-
"""seed_n9_deep_cards.py · 知识域同域深化第四批知识卡（幂等）

夜批N9（深化批次）：声学-声音三要素/光学-光的反射/生物-细胞学说/力学-摩擦力，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_sound3elem",
     "声音的三要素",
     "基础科学知识点内容（人话接口）", "声学",
     "声音的三要素：音调（声音的高低，由振动频率决定——频率越高音调越高）、"
     "响度（声音的强弱，由振幅决定——振幅越大响度越大，还与距离有关）、音色"
     "（声音的品质特色，由发声体的材料结构决定——我们能分辨不同人的声音靠的"
     "就是音色）。「闻其声知其人」靠的是音色；「引吭高歌」「低声细语」说的是响度。",
     ["声音的三要素", "音调响度音色", "音调由什么决定", "什么是音色",
      "响度与什么有关", "为什么能分辨不同人的声音"],
     ["问超声波应用", "问噪声治理"],
     "atomic", "",
     "三要素 = 音调（频率定高低）+ 响度（振幅定强弱）+ 音色（材料结构定特色，辨人靠它）。"),
    ("kp_card_lightreflect",
     "光的反射定律",
     "基础科学知识点内容（人话接口）", "光学",
     "光的反射定律：光射到物体表面时会发生反射，反射光线、入射光线和法线在同一"
     "平面内；反射光线和入射光线分居法线两侧；反射角等于入射角。反射分两种：镜面"
     "反射（平行光反射后仍平行，如平面镜）和漫反射（粗糙表面把光向四面八方反射"
     "——我们能从各方向看到不发光的物体就是靠漫反射）。两者都遵守反射定律。",
     ["光的反射定律是什么", "光的反射", "什么是镜面反射", "什么是漫反射",
      "反射角和入射角的关系", "为什么能看到不发光的物体"],
     ["问折射定律", "问平面镜成像"],
     "atomic", "",
     "反射定律 = 反射角等于入射角（三线共面、分居两侧）；镜面反射与漫反射都遵守它。"),
    ("kp_card_celltheory",
     "细胞学说",
     "基础科学知识点内容（人话接口）", "生物学",
     "细胞学说（施莱登与施旺 1838-1839 年建立）：①一切动植物都由细胞发育而来，"
     "并由细胞和细胞产物构成；②细胞是一个相对独立的单位，既有自己的生命，又对"
     "与其他细胞共同组成的整体生命起作用；③新细胞由老细胞通过分裂产生。细胞是"
     "生物体结构和功能的基本单位——这一学说揭示了动植物界的统一性，被恩格斯誉为"
     "19 世纪自然科学三大发现之一。",
     ["什么是细胞学说", "细胞学说", "细胞是谁发现的", "细胞学说的内容",
      "细胞是生物体的什么单位", "细胞学说三个要点"],
     ["问DNA细节", "问细胞分裂过程"],
     "atomic", "",
     "细胞学说 = 一切动植物由细胞构成/细胞是独立生命单位/新细胞由老细胞分裂产生——19 世纪三大发现之一。"),
    ("kp_card_friction",
     "摩擦力",
     "基础科学知识点内容（人话接口）", "力学",
     "摩擦力：两个互相接触的物体发生相对运动或有相对运动趋势时，在接触面产生的"
     "阻碍相对运动的力。方向与相对运动（趋势）方向相反。分三种：滑动摩擦（滑动"
     "时）、滚动摩擦（滚动时，远小于滑动摩擦——所以车轮优于拖拽）、静摩擦（有"
     "趋势但未动）。增大摩擦：增大压力、增大接触面粗糙程度；减小摩擦：加润滑油、"
     "变滑动为滚动、气垫悬浮。",
     ["什么是摩擦力", "摩擦力", "增大摩擦的方法", "减小摩擦的方法",
      "摩擦力的方向", "为什么车轮比拖拽省力"],
     ["问重力", "问惯性"],
     "atomic", "",
     "摩擦力 = 接触面阻碍相对运动（趋势）的力，方向相反；增大：加压/加糙；减小：润滑/滚动/气垫。"),
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
                               "level:L2", "status:verified", "batch:同域深化第四批"],
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
