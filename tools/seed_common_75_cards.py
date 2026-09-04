# -*- coding: utf-8 -*-
"""seed_common_75_cards.py · 通识拓展批次75知识卡+题库（幂等）

75：物理学-高压输电/化学-火箭燃料/生物学-仿生学/地理学-南水北调
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hvtrans",
     "高压输电：为什么电压越高损耗越小",
     "基础科学知识点内容（人话接口）", "物理学",
     "输电线上损失的功率 P损=I²R（电流的平方乘以电阻）——输送功率一定时（P=UI"
     "），**电压 U 越高，电流 I 越小**，损耗按电流的平方急剧下降（电压提高到 100"
     " 倍，电流降为 1/100，损耗降为万分之一）。所以远距离输电用高压/超高压（110"
     "kV/500kV/±800kV 特高压直流），到用户端再经变压器逐级降压（变压器只能改变"
     "交流电压——直流输电需换流站）。中国特高压技术世界领先（±1100kV 准东-皖南"
     "线，把新疆的电送到华东 3000 公里外）。相关常识：为什么鸟类站高压线不被电"
     "——两脚间电位差（跨步电压）极小，几乎无电流通过鸟体；人单脚跳过跨步电压区"
     "也是高压线落地时的自救法。",
     ["高压输电为什么能减少损耗", "特高压是什么", "变压器能改变直流电压吗",
      "鸟站在高压线上为什么没事", "跨步电压", "中国的特高压技术"],
     ["问 P损=I²R 计算", "问直流输电优缺点"],
     "atomic", "",
     "P损=I²R：同功率电压↑百倍→电流↓百倍→损耗↓万倍；远距离用超高压(±800kV+)·变压器只改交流；中国特高压世界领先；鸟不触电=两脚电位差极小。"),
    ("kp_card_rocketfuel",
     "火箭燃料",
     "基础科学知识点内容（人话接口）", "化学",
     "火箭靠燃料+氧化剂（自带氧化剂，不依赖空气——所以能在太空工作，这是与飞机"
     "喷气发动机的本质区别）燃烧喷射获得推力（反冲原理——动量守恒）。常见组合："
     "①液氢+液氧（比冲最高/最清洁，产物只有水——但需-253℃深冷储存，用于长征五"
     "号芯级）；②偏二甲肼+四氧化二氮（可常温储存，早期导弹与长征二号，但有毒）"
     "；③固体燃料（聚丁二烯类+高氯酸铵氧化剂，结构简单可长期待命——助推器/军"
     "用）。煤油液氧（长征七号）兼顾性能与成本。比冲衡量燃料效率（单位推进剂产"
     "生的冲量）。神舟飞船逃逸塔用固体火箭——事故时 3 秒把飞船拽离危险区。",
     ["火箭用什么燃料", "火箭和飞机发动机的区别", "液氢液氧的优点",
      "什么是比冲", "固体燃料和液体燃料的区别", "逃逸塔是什么"],
     ["问齐奥尔科夫斯基公式", "问可回收火箭技术"],
     "atomic", "",
     "火箭=自带氧化剂(区别于飞机·太空可用)；组合：液氢液氧(最高比冲·长五)/偏二甲肼+N₂O₄(常温·毒)/固体(待命·助推·逃逸塔)；推力=反冲(动量守恒)；煤油液氧平衡性价比。"),
    ("kp_card_bionics",
     "仿生学：向自然偷师",
     "基础科学知识点内容（人话接口）", "生物学",
     "仿生学模仿生物的结构与原理发明创造：①雷达←蝙蝠回声定位；②飞机机翼←鸟"
     "翼（更大胆的：直升机思路←蜻蜓）；③潜水艇←鱼鳔调节浮沉；④尼龙搭扣（魔"
     "术贴）←苍耳果实倒钩挂动物皮毛（瑞士工程师遛狗发现的）；⑤薄壳建筑←蛋壳"
     "（受力均匀抗压）；⑥ LED 高效发光←萤火虫冷光思路；⑦防潜水服←鲨鱼皮盾鳞"
     "减阻（鲨鱼皮泳衣曾破大量纪录后被禁）；⑧中国高铁头型←翠鸟喙（解决进出隧"
     "道音爆——新干线500系「尖头」即仿翠鸟，工程师是观鸟爱好者）。仿生学由美国"
     "斯蒂尔 1960 年正式命名——「模仿生物的科学」。",
     ["雷达模仿了什么动物", "仿生学的例子", "魔术贴是从什么得到的灵感",
      "高铁车头模仿了哪种鸟", "什么是仿生学", "鲨鱼皮泳衣为什么被禁"],
     ["问仿生材料前沿", "问莲叶效应自清洁"],
     "atomic", "",
     "仿生学(1960 斯蒂尔命名)：雷达←蝙蝠/搭扣←苍耳倒钩/薄壳建筑←蛋壳/高铁头型←翠鸟喙(消音爆)/鲨鱼皮泳衣(破纪录后被禁)/潜水艇←鱼鳔。"),
    ("kp_card_snwd",
     "南水北调工程",
     "人文通识知识点内容（人话接口）", "地理学",
     "南水北调：把长江流域的水调往缺水的华北与西北——中国最大调水工程，分东/"
     "中/西三条线路：①东线——从江苏扬州江都取长江水，沿京杭大运河北上（13 级"
     "泵站提水），送达山东天津（2013 通水）；②中线——从丹江口水库（汉江）自流"
     "北上经河南、河北到北京天津（2014 通水，京津冀豫沿线主力水源——水质好、"
     "全程自流）；③西线（规划中）——从长江上游调水入黄河上游，工程难度最大尚"
     "未实施。意义：缓解华北水资源危机（北京城区七成供水为南水）、地下水超采回"
     "补、生态改善。总调水量超 500 亿立方米（相当于一条黄河的水量）。丹江口水库"
     "为中线水源地，保护严格。",
     ["南水北调分几条线路", "中线工程的水源地", "南水北调东线沿什么河",
      "为什么中线能自流", "南水北调的意义", "西线为什么还没实施"],
     ["问京杭大运河史", "问水资源调配其他案例"],
     "atomic", "",
     "南水北调三线：东线(扬州→京杭运河·13 级泵站·2013)/中线(丹江口→京津·自流·2014·主力)/西线(规划)；缓解华北缺水·回补地下水；调水超 500 亿 m³≈一条黄河。"),
]

QUESTIONS = [
    ("QB-433", "高压输电为什么能减少损耗", "物理学", "技术直答",
     ["电压", "电流", "损耗"], "通识拓展75"),
    ("QB-434", "火箭用什么燃料", "化学", "技术直答",
     ["液氢", "液氧", "氧化剂"], "通识拓展75"),
    ("QB-435", "雷达模仿了什么动物", "生物学", "技术直答",
     ["蝙蝠"], "通识拓展75"),
    ("QB-436", "南水北调分几条线路", "地理学", "技术直答",
     ["东线", "中线", "西线", "三条"], "通识拓展75"),
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
                               "level:L2", "status:verified", "batch:通识拓展75"],
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
    bank["version"] = "v1.67"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
