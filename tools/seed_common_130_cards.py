# -*- coding: utf-8 -*-
"""seed_common_130_cards.py · 通识拓展批次130知识卡+题库（幂等）

130：物理学-抛体运动与体育/生活常识-家电清洗保养/地理学-中国地理之最综合
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_projangle",
     "抛体运动与体育",
     "基础科学知识点内容（人话接口）", "物理学",
     "抛体运动在体育中的应用：①**投掷类**——铅球/标枪/铁饼的最佳出手角度约"
     "**40-42°**（理论无空气阻力时 45° 最远，但实际出手高度高于落地点+空气阻"
     "力，最佳角度略小）；②**篮球投篮**——抛物线弧度越高越容易入筐（高弧度下"
     "落速度快、入筐有效面积大——「空心球」）；③**跳远**——起跳角度约 18-24°"
     "（非 45°，因助跑水平速度贡献大，不能牺牲速度换取角度）；④足球任意球——"
     "香蕉球（马格努斯效应：旋转球体两侧气流速度不同产生侧向力）。物理与运动训"
     "练结合就是运动生物力学。",
     ["投掷铅球的最佳角度是多少", "篮球投篮的抛物线", "跳远的最佳起跳角度",
      "香蕉球的物理原理", "马格努斯效应", "运动生物力学"],
     ["问45度射程最远证明", "问空气阻力影响"],
     "atomic", "",
     "抛体运动体育应用：铅球最佳角 40-42°(非45°因出手高度+阻力)/篮球高弧易入筐/跳远 18-24°(不能牺牲速度)/香蕉球=马格努斯效应(旋转侧向力)。"),
    ("kp_card_appclean",
     "家电的清洗与保养",
     "生活常识知识点内容（人话接口）", "生活常识",
     "常用家电清洗保养：①**空调**——每 1-2 个月清洗滤网（脏堵降低制冷效果+耗电"
     "增加 15%++滋生细菌吹出异味）；②**洗衣机**——每 3 个月用洗衣机清洁剂清洗内"
     "筒夹层（藏污纳垢+霉菌异味——「洗衣机比马桶脏」是真的）；③**冰箱**——每"
     "月擦拭内壁+密封条（发霉密封条致制冷不良），化霜除冰；④**油烟机**——每 3-6"
     " 个月深度清洗油网（油垢堵塞影响吸烟效果+火灾隐患）；⑤**电热水壶**——白醋"
     "煮沸除水垢（碳酸钙+醋酸反应）；⑥**电视机**——干布擦屏（勿用湿布/酒精——"
     "损伤涂层）。定期清洗=省电+延长寿命+健康。",
     ["家电清洗保养方法", "空调滤网多久洗一次", "洗衣机怎么清洗",
      "冰箱密封条发霉怎么办", "电热水壶除水垢", "油烟机多久清洗一次"],
     ["问家电清洗服务", "问家电保养误区"],
     "atomic", "",
     "家电保养=空调滤网 1-2 月/洗衣机 3 月清洗内筒/冰箱月擦+化霜/油烟机半年深度洗/水壶白醋除垢；脏堵→耗电增+细菌+寿命短——定期清洗=省电+健康+耐用。"),
    ("kp_card_chinasuper2",
     "中国地理之最综合",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国地理之最大盘点：①面积最大的省级行政区——新疆维吾尔自治区（约 166 万"
     "km²）；②人口最多的省——广东（常住人口超 1.26 亿）；③最大的城市——上海"
     "（城区人口）；④最大的淡水湖——鄱阳湖（江西）；⑤最大的咸水湖——青海湖"
     "（约 4600km²）；⑥最长的河流——长江（6300km）；⑦最高的山峰——珠穆朗玛峰"
     "（8848.86m）；⑧最大的盆地——塔里木盆地（约 53 万km²）；⑨最大的平原——东"
     "北平原（约 35 万km²）；⑩最深的峡谷——雅鲁藏布大峡谷（最深 6009m）；⑪最大"
     "的瀑布——黄果树瀑布（贵州）；⑫最高的宫殿——布达拉宫（海拔约 3700m）。",
     ["中国面积最大的省级行政区", "中国最长的河流", "中国最大的淡水湖",
      "中国最深的峡谷", "中国最大的平原", "中国最大的瀑布在哪里"],
     ["问世界之最对比", "问中国地理分区"],
     "atomic", "",
     "中国地理之最=新疆最大省级(166 万km²)+鄱阳最大淡水湖+青海湖最大咸水湖+长江最长河 6300km+珠峰最高 8848.86m+塔里木最大盆+东北最大平原+雅鲁藏布最深谷 6009m+黄果树最大瀑布+布达拉宫最高宫殿。"),
]

QUESTIONS = [
    ("QB-656", "投掷铅球的最佳角度是多少", "物理学", "技术直答",
     ["40", "45"], "通识拓展130"),
    ("QB-657", "家电清洗保养方法", "生活常识", "技术直答",
     ["空调滤网", "洗衣机", "冰箱"], "通识拓展130"),
    ("QB-658", "中国面积最大的省级行政区", "地理学", "技术直答",
     ["新疆"], "通识拓展130"),
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
                               "level:L2", "status:verified", "batch:通识拓展130"],
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
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.3"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
