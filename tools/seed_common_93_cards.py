# -*- coding: utf-8 -*-
"""seed_common_93_cards.py · 通识拓展批次93知识卡+题库（幂等）

93：物理学-导体与绝缘体/化学-化学方程式的含义/生物学-输血与血量/地理学-黄土高原水土流失
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_condinsu",
     "导体与绝缘体",
     "基础科学知识点内容（人话接口）", "物理学",
     "容易导电的物体叫**导体**：金属（自由电子导电）、人体、大地、酸碱盐水溶液、"
     "石墨——导电靠自由电荷（金属中是自由电子）。不容易导电的叫**绝缘体**：橡"
     "胶、玻璃、塑料、陶瓷、油、干燥的木头/空气——电荷几乎被束缚。没有绝对界限："
     "「导体」与「绝缘体」在一定条件下可转化——玻璃加热到红热状态会导电、干木"
     "头潮湿后导电（潮湿的手不能碰电器！）、纯水不导电而普通水导电（含杂质离"
     "子）。半导体介于两者之间且可控（semicond 呼应）。安全应用：电工用带绝缘柄"
     "的工具、高压线是裸线但悬挂在绝缘瓷瓶上、湿手不触开关（人体是导体+水降低电"
     "阻增大危险）。",
     ["导体和绝缘体的区别", "金属靠什么导电", "导体和绝缘体能转化吗",
      "潮湿的木头为什么能导电", "纯水能导电吗", "电工工具为什么要绝缘柄"],
     ["问电阻率排序", "问安全用电复习"],
     "atomic", "",
     "导体=金属(自由电子)/人体/大地/酸碱盐溶液/石墨；绝缘体=橡胶玻璃陶瓷油干木；无绝对界限可转化(玻璃红热导电·木头潮湿导电)；湿手勿触电=人体导体+阻降。"),
    ("kp_card_equmean",
     "化学方程式的含义",
     "基础科学知识点内容（人话接口）", "化学",
     "化学方程式 C + O₂ →(点燃) CO₂ 的三层含义：①**质**的意义——表明反应物"
     "（碳和氧气）、生成物（二氧化碳）、反应条件（点燃）；②**量**的意义——各物"
     "质间质量比固定：12 : 32 : 44（相对质量比），「每 12 份质量的碳与 32 份质量的"
     "氧气完全反应生成 44 份二氧化碳」；③**粒子**的意义——每 1 个碳原子与 1 个"
     "氧分子（含 2 个氧原子）反应生成 1 个二氧化碳分子。书写原则：以客观事实为基"
     "础（不能臆造）、遵守质量守恒定律（必须配平）。配平方法：最小公倍数法/观察"
     "法。读法示例：「碳和氧气在点燃条件下反应生成二氧化碳」。",
     ["化学方程式的含义", "化学方程式怎么读", "配平化学方程式的原则",
      "质量守恒在方程式中怎么体现", "化学方程式的三种意义", "最小公倍数法配平"],
     ["问相对分子质量计算", "问根据方程式计算"],
     "atomic", "",
     "方程式三层义=质(反应物生成物条件)+量(固定质量比 12:32:44)+粒子(1 原子+1 分子→1 分子)；原则=客观事实+配平(质量守恒)；读法「和→在→条件下→生成」。"),
    ("kp_card_transfusion",
     "输血与血量",
     "基础科学知识点内容（人话接口）", "生物学",
     "成年人的血量约为体重的 7%-8%（50kg 的人约 4000ml）——一次失血超过 800-"
     "1000ml 会头晕心跳加快、超过 1200-1500ml 有生命危险需输血。健康成年人一次"
     "献血 **200-300ml** 不影响健康（失血的水和无机盐 1-2 小时内恢复、血浆蛋白"
     "约 1-2 天恢复、红细胞约一个月恢复），且适量献血刺激造血。输血原则：以输**"
     "同型血**为原则（ABO 血型——bloodtype 呼应）；无同型血的紧急情况 O 型可少量"
     "输给其他型（「万能供血者」的说法有限定条件）、AB 型可接受少量其他型（「万"
     "能受血者」）。成分输血：缺什么补什么（血小板减少输血小板、贫血输红细胞）"
     "——更高效安全，是现代输血主流。6 月 14 日世界献血者日。",
     ["健康成年人一次献血多少不影响健康", "输血的原则是什么", "献血后血细胞多久恢复",
      "什么是成分输血", "血量占体重的比例", "世界献血者日"],
     ["问血型遗传常识", "问献血条件与健康"],
     "atomic", "",
     "血量≈体重 7-8%(50kg≈4000ml)；献血 200-300ml 无碍(血浆 1-2 天/红细胞 1 月恢复)；输血=同型原则(应急 O 供/AB 受少量)+成分输血(缺啥补啥)；6.14 献血者日。"),
    ("kp_card_loess",
     "黄土高原的水土流失",
     "人文通识知识点内容（人话接口）", "地理学",
     "黄土高原（陕西/山西/甘肃等，面积约 64 万平方公里）是世界上水土流失最严重"
     "的地区之一，沟壑纵横（千沟万壑支离破碎）。原因：自然——①黄土土质**疏"
     "松**（孔隙多、垂直节理发育，遇水易崩解）；②降水集中在**夏季且多暴雨**；③"
     "地形破碎坡度大、植被稀少。人为——过垦过牧、修路采矿破坏植被。危害：①土"
     "壤肥力下降农作物减产；②泥沙入黄河使下游**地上河**（河床高出两岸地面，「悬"
     "河」——开封段河床高出市区约 10 米）洪涝风险剧增；③水库淤积。治理：生物措"
     "施（植树种草——退耕还林还草）+工程措施（打坝淤地/修梯田）+小流域综合治理"
     "（「山顶戴帽子、山腰系带子、山脚穿靴子」立体模式）——成效显著黄河输沙量大"
     "幅下降。",
     ["黄土高原水土流失的原因", "黄河下游为什么是地上河", "水土流失的治理措施",
      "小流域综合治理", "黄土高原的土质特点", "地上河的危害"],
     ["问黄河调水调沙", "问退耕还林成效"],
     "atomic", "",
     "黄土高原水土流失=土松+暴雨集中+植被破坏(人为过垦)：害=贫瘠化+黄河地上河(开封高出 10m)+淤库；治=生物(还林草)+工程(坝地梯田)+小流域立体治理——输沙大降。"),
]

QUESTIONS = [
    ("QB-505", "导体和绝缘体的区别", "物理学", "技术直答",
     ["自由电荷", "导电"], "通识拓展93"),
    ("QB-506", "化学方程式的含义", "化学", "技术直答",
     ["质量守恒", "配平"], "通识拓展93"),
    ("QB-507", "健康成年人一次献血多少不影响健康", "生物学", "技术直答",
     ["200", "300ml"], "通识拓展93"),
    ("QB-508", "黄土高原水土流失的原因", "地理学", "技术直答",
     ["土质疏松", "暴雨", "植被"], "通识拓展93"),
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
                               "level:L2", "status:verified", "batch:通识拓展93"],
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
    bank["version"] = "v1.85"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
