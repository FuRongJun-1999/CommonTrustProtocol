# -*- coding: utf-8 -*-
"""seed_common_65_cards.py · 通识拓展批次65知识卡+题库（幂等）

65：物理学-声的利用/化学-酒精灯的使用/生物学-生物分类等级/生活常识-含氟牙膏
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_sounduse",
     "声音的两类利用：传信息与传能量",
     "基础科学知识点内容（人话接口）", "物理学",
     "声音能传递**信息**（B超检查/声呐探鱼测深/回声定位/敲西瓜听生熟/医生听诊"
     "器）也能传递**能量**（超声波碎石——击碎肾结石、超声清洗眼镜首饰、超声波"
     "除尘）。区分口诀：探知情况=信息、改变物体=能量。超声波（>20000Hz）：方向"
     "性好穿透强——B超/声呐/清洗；次声波（<20Hz）：传播远穿透强——地震/海啸/"
     "台风监测（动物先于人感知次声波异常）、次声武器探索。声呐原理=回声测距（发出"
     "超声波→接收回波→s=vt/2）；B超用超声不用声波是因为超声频率高方向性好。"
     "回声测距需障碍物距离≥17 米才能区分回声与原声。",
     ["B超利用声可以传递什么", "声的利用有哪些", "超声波和次声波的区别",
      "声呐的工作原理", "超声波能碎石吗", "为什么用超声波做B超"],
     ["问多普勒超声测血流", "问次声监测网"],
     "atomic", "",
     "声两用：传信息(B超/声呐/听诊/敲瓜)与传能量(碎石/清洗)；超声>20000Hz 方向好·次声<20Hz 传得远(灾害监测)；声呐=回声测距 s=vt/2；17m 才能分辨回声。"),
    ("kp_card_alcohollamp",
     "酒精灯的正确使用",
     "基础科学知识点内容（人话接口）", "化学",
     "酒精灯使用规范：①点燃——用火柴/打火机从侧面点燃，**禁止用一盏酒精灯去引"
     "燃另一盏**（倾斜时酒精溢出引燃）；②熄灭——**用灯帽盖灭，不可用嘴吹**（吹"
     "气可能把火焰压入灯内引燃灯内酒精蒸气，甚至爆炸；盖灭后再重盖一次放气防压"
     "力打不开）；③加热——用外焰（温度最高，酒精灯火焰分外焰/内焰/焰心三层）；"
     "④添加酒精——必须熄灭后进行，不超过容积 2/3、不少于 1/4；⑤万一洒出着火"
     "——立即用湿抹布盖灭。外焰温度约 500-700℃（酒精完全燃烧区）。与酒精喷灯"
     "区别：喷灯温度更高（约 1000℃，用于玻璃加工）。",
     ["酒精灯不能用嘴吹灭", "酒精灯火焰哪层温度最高", "为什么不能对点燃酒精灯",
      "酒精灯里酒精加多少合适", "酒精灯着火怎么办", "酒精灯外焰温度"],
     ["问实验室安全守则", "问火焰结构对比"],
     "atomic", "",
     "酒精灯：点燃用火柴禁互引；熄灭用灯帽禁嘴吹(防引燃灯内蒸气·盖后重盖放气)；加热用外焰(500-700℃)；酒精 1/4~2/3·熄灯再加；洒火湿抹布盖。"),
    ("kp_card_taxonomy",
     "生物分类的等级",
     "基础科学知识点内容（人话接口）", "生物学",
     "生物分类从大到小七个等级：**界、门、纲、目、科、属、种**——分类单位越小，"
     "包含生物越少，共同特征越多、亲缘关系越近；「种」是最基本的分类单位（同种"
     "生物可交配繁殖有生殖能力的后代）。例：家猫——动物界/脊索动物门/哺乳纲/食"
     "肉目/猫科/猫属/猫种；人类——动物界/脊索动物门/哺乳纲/灵长目/人科/人属/"
     "智人种。分类学家：林奈（双命名法：属名+种加词，拉丁文斜体，如 Homo "
     "sapiens）。五界系统：原核生物界/原生生物界/真菌界/植物界/动物界（病毒无细"
     "胞结构单独论）。植物分类主要依据：花、果实、种子（生殖器官比根茎叶更稳"
     "定）。",
     ["生物分类的基本单位是什么", "生物分类从大到小的等级", "林奈的贡献",
      "双命名法是什么", "人属于什么纲什么目", "植物分类为什么看花和果实"],
     ["问检索表使用", "问病毒分类争议"],
     "atomic", "",
     "七等级=界门纲目科属种(越小共同特征越多)；种=基本单位(可育后代)；林奈双命名法(属+种·拉丁斜体 Homo sapiens)；五界系统；植物分类看生殖器官(花果种子)。"),
    ("kp_card_fluoride",
     "含氟牙膏与龋齿预防",
     "生活常识知识点内容（人话接口）", "生活常识",
     "含氟牙膏防龋齿的原理：氟离子与牙釉质（羟基磷灰石）结合生成更耐酸的氟磷灰"
     "石，并促进釉质再矿化——修复早期脱矿、抵抗酸的腐蚀。氟化物双刃剑：适量防"
     "龋，过量致**氟斑牙**（牙齿发黄褐斑，恒牙发育期即儿童 8 岁前摄入过量）和氟"
     "骨症（长期大量）——高氟地区（饮水含氟高）反而要选无氟牙膏（我国山西/内蒙"
     "古部分地区），儿童用含氟牙膏要控制用量（米粒大小）并监督不吞咽。刷牙之外"
     "防龋：窝沟封闭（磨牙咬合面涂封剂）、少吃糖尤其睡前、定期检查。含氟量标准："
     "成人牙膏氟浓度约 1000-1500 ppm（0.1%-0.15%）。",
     ["含氟牙膏有什么作用", "氟斑牙是怎么回事", "高氟地区能用含氟牙膏吗",
      "儿童怎么用含氟牙膏", "窝沟封闭是什么", "蛀牙怎么预防"],
     ["问牙釉质再矿化研究", "问饮水加氟争议"],
     "atomic", "",
     "含氟牙膏=氟离子→氟磷灰石耐酸+再矿化→防龋；过量→氟斑牙(8 岁前)/氟骨症——高氟地区选无氟；儿童米粒量防吞咽；搭档=窝沟封闭+少糖+定期检查。"),
]

QUESTIONS = [
    ("QB-393", "B超利用声可以传递什么", "物理学", "技术直答",
     ["信息"], "通识拓展65"),
    ("QB-394", "酒精灯不能用嘴吹灭", "化学", "技术直答",
     ["灯帽", "引燃"], "通识拓展65"),
    ("QB-395", "生物分类的基本单位是什么", "生物学", "技术直答",
     ["种"], "通识拓展65"),
    ("QB-396", "含氟牙膏有什么作用", "生活常识", "技术直答",
     ["防龋齿"], "通识拓展65"),
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
                               "level:L2", "status:verified", "batch:通识拓展65"],
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
    bank["version"] = "v1.57"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
