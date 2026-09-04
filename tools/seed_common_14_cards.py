# -*- coding: utf-8 -*-
"""seed_common_14_cards.py · 通识拓展批次知识卡（幂等）

14：天文学-望远镜类型/交通-交通工具的演进/化学-常见化学反应类型/建筑-世界著名建筑
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_telescope",
     "望远镜的类型与原理",
     "基础科学知识点内容（人话接口）", "天文学",
     "望远镜的类型：①折射望远镜（用透镜汇聚光线，伽利略1609年首次用于观天——"
     "色差较大）；②反射望远镜（用凹面镜汇聚光线，无色差——哈勃太空望远镜属于"
     "此类）；③射电望远镜（接收天体发出的无线电波，如中国天眼FAST——世界最大"
     "单口径射电望远镜500米口径）。太空望远镜（哈勃/韦布）在大气层外观测，避"
     "免大气扰动，可看到更遥远更清晰的天体。",
     ["望远镜的类型", "折射望远镜和反射望远镜", "中国天眼", "哈勃望远镜",
      "射电望远镜", "韦布太空望远镜"],
     ["问宇宙探索", "问系外行星"],
     "atomic", "",
     "望远镜三型 = 折射（透镜）/反射（凹面镜）/射电（无线电波）；太空望远镜避开大气扰动最清晰。"),
    ("kp_card_transport",
     "交通工具的演进",
     "人文通识知识点内容（人话接口）", "交通史",
     "交通工具的演进：马车（数千年前）→蒸汽火车（1804史蒂芬孙）→汽车（1886"
     "卡尔·本茨内燃机）→飞机（1903莱特兄弟首飞12秒36米）→高铁（时速350km+" 
     "磁悬浮试验603km）→喷气客机→宇宙飞船。每次交通革命都大幅缩短时空距离："
     "从北京到广州古代骑马数月→火车数天→飞机3小时。中国高铁运营里程世界第一"
     "（超4万公里）。",
     ["交通工具的演进", "交通发展史", "飞机是谁发明的", "蒸汽火车",
      "中国高铁", "交通工具的变化"],
     ["问汽车发明", "问航海史"],
     "atomic", "",
     "交通工具演进 = 马车→蒸汽火车→汽车→飞机→高铁→飞船；每次革命缩短时空距离；中国高铁里程世界第一。"),
    ("kp_card_chemrxn",
     "常见的化学反应类型",
     "基础科学知识点内容（人话接口）", "化学",
     "四种基本化学反应类型：化合反应（多变一：A+B→AB，如铁+氧气→四氧化三"
     "铁）；分解反应（一变多：AB→A+B，如水通电分解为氢气和氧气）；置换反应"
     "（单质+化合物→新单质+新化合物，如铁+硫酸铜→铜+硫酸亚铁）；复分解反应"
     "（两种化合物交换成分，如酸碱中和）。氧化反应不属于四大基本类型但极为常"
     "见（燃烧、生锈等）。",
     ["常见的化学反应类型", "化合反应", "分解反应", "置换反应", "复分解反应",
      "化学反应的基本类型", "氧化反应"],
     ["问化学方程式配平", "问离子反应"],
     "atomic", "",
     "四大反应 = 化合（多变一）/分解（一变多）/置换（单质换单质）/复分解（交换成分）。"),
    ("kp_card_worldbuildings",
     "世界著名建筑",
     "人文通识知识点内容（人话接口）", "建筑学",
     "世界著名建筑：中国——长城（防御工程/万里绵延）、故宫（最大木结构宫殿群"
     "）、赵州桥（最古老的敞肩石拱桥）；外国——埃及金字塔（约4500年/胡夫金字"
     "塔高约146.5m）、希腊帕特农神庙（多立克柱式代表）、罗马斗兽场（古罗马建"
     "筑巅峰）、印度泰姬陵（白色大理石陵墓）、法国埃菲尔铁塔（1889年/300m 铁"
     "塔）、悉尼歌剧院（帆船造型现代建筑）。",
     ["世界著名建筑", "长城", "埃及金字塔", "泰姬陵", "埃菲尔铁塔",
      "悉尼歌剧院", "著名建筑有哪些"],
     ["问哥特式建筑", "问现代建筑"],
     "atomic", "",
     "著名建筑 = 长城（防御）/金字塔（陵墓）/帕特农（神庙）/斗兽场（竞技）/泰姬陵（陵墓）/埃菲尔铁塔/悉尼歌剧院。"),
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
                               "level:L2", "status:verified", "batch:通识拓展14"],
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
