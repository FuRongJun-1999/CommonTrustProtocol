# -*- coding: utf-8 -*-
"""seed_common_53_cards.py · 通识拓展批次53知识卡+题库（幂等）

53：物理学-体温计的缩口/生活常识-防晒霜SPF/生物学-骨关节肌肉运动/地理学-地图三要素
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_thermo",
     "体温计为什么可以离开人体读数",
     "基础科学知识点内容（人话接口）", "物理学",
     "普通液体温度计不能离开被测物体读数（一离开示数就变），体温计却可以——因"
     "为玻璃泡上方有一个特殊的**缩口**（很细的弯管）：体温上升时水银胀过缩口上"
     "升；离开人体后水银遇冷收缩，在缩口处断开、上面的水银退不回来，示数保持不"
     "变。所以用前要「甩一甩」——把水银甩回玻璃泡（普通温度计绝不能甩）。体温计"
     "量程 35-42℃（人体温范围，分度值 0.1℃ 更精细）。正常体温约 36-37℃（腋"
     "下），发热分级：低热 37.3-38℃、高热 39℃ 以上。其他测温：额温枪（红外感"
     "应热辐射，非接触）、电子体温计（热敏电阻）。水银体温计摔碎要开窗通风+硫磺"
     "粉处理（汞有毒）。",
     ["体温计为什么可以离开人体读数", "体温计的缩口原理", "体温计用前为什么要甩",
      "体温计的量程和分度值", "正常体温是多少", "额温枪的原理"],
     ["问电子温度计传感", "问水银泄漏处理规范"],
     "atomic", "",
     "体温计可离体读数=缩口(水银冷缩断开退不回)；用前甩一甩(普通温度计禁甩)；量程 35-42℃·分度 0.1℃；正常腋温 36-37℃；额温枪=红外热辐射。"),
    ("kp_card_spf",
     "防晒霜的 SPF 与防晒原理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "阳光中伤皮肤的主要是紫外线：UVB（中波，晒红晒伤、参与合成维生素D）和 UVA"
     "（长波，晒黑晒老、可穿透玻璃）。SPF（Sun Protection Factor）主要防 UVB："
     "表示防护时长的倍数——不涂约 15 分钟晒红，SPF30 理论约可防 30 倍时长（450"
     " 分钟）；PA+~PA++++ 防晒黑（防 UVA 强度分级）。防晒霜两条路线：物理防晒"
     "（氧化锌/二氧化钛反射散射紫外线，温和适合敏感肌）与化学防晒（有机物吸收紫"
     "外线转化为热，肤感清爽但可能刺激）。正确用法：出门前 15-20 分钟涂、量要足"
     "（面部约一元硬币大小）、每 2 小时补涂、阴天也要防（UVA 穿云）。硬防晒="
     "伞/帽/防晒衣（UPF 标识）更可靠。",
     ["防晒霜的SPF是什么意思", "UVA和UVB有什么区别", "物理防晒和化学防晒的区别",
      "PA加号越多代表什么", "防晒霜怎么涂才正确", "阴天需要防晒吗"],
     ["问紫外线波段划分", "问防晒衣UPF标准"],
     "atomic", "",
     "UVB 晒红(合成VD)/UVA 晒黑老(穿玻璃)；SPF=防 UVB 时长倍数、PA=防 UVA 强度；物理(氧化锌反射)vs 化学(吸收)；出门前 15-20min·2h 补涂·阴天也要防。"),
    ("kp_card_joints",
     "骨、关节与肌肉：运动的杠杆",
     "基础科学知识点内容（人话接口）", "生物学",
     "人体的运动系统=骨（杠杆）+关节（支点）+骨骼肌（动力）：肌肉收缩牵动骨绕关"
     "节活动——屈肘时肱二头肌收缩、肱三头肌舒张（伸肘相反），两组肌肉配合像双向"
     "拉索。关节结构：关节面（覆盖关节软骨减少摩擦）、关节囊、关节腔（滑液润滑）"
     "——关节炎多因软骨磨损/滑液异常。人体主要关节：肩（最灵活）、髋（最稳定承"
     "重）、膝（最大最复杂，半月板缓冲）。脱臼=关节头从关节窝滑出；青少年骨骼"
     "柔韧但骺软骨未闭合（长个子期间），运动前热身防拉伤。人体骨骼肌 600 多块，"
     "最强大的肌肉是股四头肌群。",
     ["人运动的杠杆支点动力分别是什么", "屈肘时肱二头肌是什么状态",
      "关节的基本结构", "脱臼是怎么回事", "人体最灵活的关节", "半月板的作用"],
     ["问肌肉收缩分子机制", "问运动损伤处理"],
     "atomic", "",
     "运动系统=骨(杠杆)+关节(支点)+骨骼肌(动力)；屈肘=肱二头肌收/三头肌舒(伸肘相反)；关节=面囊腔+软骨滑液减摩；肩最灵活/膝最大；脱臼=头出窝。"),
    ("kp_card_map3",
     "地图的三要素",
     "人文通识知识点内容（人话接口）", "地理学",
     "看懂地图的三要素：①比例尺——图上距离与实际距离之比（数字式 1:100000、"
     "线段式、文字式），分母越大比例尺越小、表示范围越大越简略（世界地图 vs 社"
     "区图）；②方向——一般定向法「上北下南左西右东」，指向标定向法（箭头指"
     "北），经纬网定向法（最准确，经线指示南北纬线指示东西）；③图例和注记——图"
     "例是符号说明（河流线/铁路黑白相间线/城市圆圈），注记是文字与数字。拓展：等"
     "高线地形图读地形——等高线密集=坡陡、稀疏=坡缓，闭合等高线数值内大=山顶、"
     "内小=盆地，等高线重叠=陡崖。手机导航用的是电子地图+GPS/北斗定位（比例尺动"
     "态缩放）。",
     ["地图的三要素是什么", "比例尺越大表示范围越大吗", "怎么在地图上看方向",
      "等高线密集说明什么", "什么是图例", "电子地图和纸质地图的区别"],
     ["问等高线地形判读进阶", "问北斗卫星定位"],
     "atomic", "",
     "地图三要素=比例尺(分母大→范围大更简略)+方向(上北下南/指向标/经纬网)+图例注记；等高线密=坡陡·闭合内大=山顶·重叠=陡崖；导航=电子图+北斗GPS。"),
]

QUESTIONS = [
    ("QB-345", "体温计为什么可以离开人体读数", "物理学", "技术直答",
     ["缩口"], "通识拓展53"),
    ("QB-346", "防晒霜的SPF是什么意思", "生活常识", "技术直答",
     ["防晒时长", "UVB"], "通识拓展53"),
    ("QB-347", "人运动的杠杆支点动力分别是什么", "生物学", "技术直答",
     ["骨", "关节", "肌肉"], "通识拓展53"),
    ("QB-348", "地图的三要素是什么", "地理学", "技术直答",
     ["比例尺", "方向", "图例"], "通识拓展53"),
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
                               "level:L2", "status:verified", "batch:通识拓展53"],
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

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.45"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
