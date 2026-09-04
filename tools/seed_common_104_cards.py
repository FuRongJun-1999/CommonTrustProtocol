# -*- coding: utf-8 -*-
"""seed_common_104_cards.py · 通识拓展批次104知识卡+题库（幂等）

104：物理学-误差与错误/化学-实验室安全/生物学-微生物与食品制作/地理学-中国四大地理区域
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_errorvs",
     "误差与错误",
     "基础科学知识点内容（人话接口）", "物理学",
     "**误差**：测量值与真实值之间的差异——**不可消除**（测量工具精度有限、测量"
     "者估读、环境温度等固有因素），只能**减小**：多次测量求平均值、选用精密仪"
     "器、改进测量方法。**错误**：不遵守操作规则引起（读数时视线不垂直、天平左"
     "码右物读反）——**可以避免**，也不该发生。区别一句话：误差不可避免、错误可"
     "以避免；「误差不是错误」。例：多次测量长度求平均值是减小误差；把厘米刻度"
     "读错是错误。拓展：有效数字（记录到分度值下一位——估读位）；测量 specialization"
     "：精密仪器（激光干涉测长、原子钟计时 2000 万年差 1 秒）也只是减小误差而非"
     "消灭。",
     ["误差可以消除吗", "误差和错误的区别", "怎么减小误差",
      "多次测量求平均值", "什么是有效数字", "读数视线不垂直是什么"],
     ["问平均值计算规范", "问精密测量仪器"],
     "atomic", "",
     "误差=测量值与真值差·不可消除只能减小(多次平均/精密仪器/改进方法)；错误=违规造成·可避免不该发生；口诀「误差不是错误」；记录到分度值下一位=估读位。"),
    ("kp_card_labsafe",
     "化学实验室安全守则",
     "基础科学知识点内容（人话接口）", "化学",
     "化学实验室安全核心守则：①**进入实验室**——穿实验服、戴护目镜，长发束起，"
     "不饮食不追逐打闹；②**药品取用**——三不原则：不能用手接触药品、不能把鼻孔"
     "凑到容器口闻气味（扇闻）、不得尝任何药品的味道；按需取用，剩药不放回原瓶"
     "（防污染）；③**加热操作**——试管外壁擦干、液体不超 1/3、管口不对人、先预"
     "热再集中加热；④**酸碱使用**——酸入水（稀释浓硫酸必须把酸沿器壁缓慢加入水"
     "中并搅拌，绝不能水入酸——暴沸飞溅）；溅到皮肤立即大量清水冲洗；⑤**意外处"
     "理**——酒精洒出燃烧用湿抹布盖、酸碱入眼立即水洗就医；⑥**结束**——洗净手、"
     "关水电气、废液入指定回收缸（不直接倒入下水道）。",
     ["化学实验室安全守则", "药品的三不原则", "稀释浓硫酸要注意什么",
      "酒精灯打翻了怎么办", "酸溅到皮肤上怎么办", "剩的药品能放回原瓶吗"],
     ["问废液分类回收", "问防护装备标准"],
     "atomic", "",
     "实验室安全：三不原则(不触不闻不尝)+剩药不回瓶；稀释浓硫酸=酸入水搅拌(禁水入酸)；酒精火湿抹布盖；酸入眼水洗就医；废液入回收缸不倒下水道。"),
    ("kp_card_microbiofood",
     "微生物与食品制作",
     "基础科学知识点内容（人话接口）", "生物学",
     "微生物是食品制作的「隐形厨师」：①**酵母菌**（真菌）——面包/馒头（产 CO₂"
     "蓬松）+酿酒（产酒精，无氧时酒精发酵）；②**乳酸菌**（细菌）——酸奶/泡菜/酸"
     "黄瓜（乳糖→乳酸，抑制杂菌，所以泡菜坛要密封——乳酸菌厌氧）；③**醋酸菌"
     "**——酿醋（酒精→醋酸，需氧）；④**霉菌**——酱油/豆豉/腐乳（米曲霉等）、"
     "蓝纹奶酪（青霉）。原理共性：微生物酶分解原料中的糖/蛋白/脂肪，产生风味物"
     "质并抑制腐败菌。控制关键：菌种、温度、盐度、氧气（有氧无氧决定产物——酵母"
     "有氧产 CO₂ 无氧产酒精）。防腐对垒：巴氏消毒（奶）、高温灭菌（罐头）、真空/"
     "充氮（隔绝需氧菌）、冷藏冷冻（抑菌）。",
     ["微生物在食品制作中的应用", "酿酒用什么微生物", "泡菜坛为什么要密封",
      "酿醋的原理", "面包和馒头发酵靠什么", "食品防腐的方法有哪些"],
     ["问发酵温度控制", "问益生菌产品评测"],
     "atomic", "",
     "食品微生物：酵母(面包产气+酿酒产醇·有氧无氧产物不同)/乳酸菌(酸奶泡菜·厌氧密封)/醋酸菌(酒→醋·需氧)/霉菌(酱腐乳)；控制=菌种温度盐氧；防腐=巴氏/罐头/冷藏。"),
    ("kp_card_4regions",
     "中国四大地理区域",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国划分四大地理区域：①**北方地区**——秦岭淮河以北：温带季风气候，平原广"
     "（东北/华北），旱地小麦杂粮，暖温带落叶阔叶林，民居平顶注重保温；②**南方"
     "地区**——秦岭淮河以南：亚热带/热带季风气候，水田水稻，河湖密布「鱼米之"
     "乡」，尖顶屋利排水；③**西北地区**——大兴安岭以西：深居内陆干旱，草原荒"
     "漠，畜牧业+灌溉农业（绿洲）；④**青藏地区**——海拔 4000 米+：高寒，河谷农"
     "业（青稞），高寒牧业（牦牛），日照强太阳能丰富。划分依据：气候（气温与降"
     "水）+地形——北方南方界=秦岭淮河（气候）；西北北方界=400mm 等降水量线（季"
     "风区界）；青藏界=地势一二级阶梯界线（昆仑-祁连-横断山）。区域差异是「综合"
     "思维+区域认知」地理素养的核心。",
     ["中国四大地理区域怎么划分", "北方和南方的分界线", "西北地区的界线",
      "青藏地区的范围", "四大区域划分的依据", "各区域的农业类型"],
     ["问区域发展差异", "问区域联动发展"],
     "atomic", "",
     "四大区域=北方(秦淮北·旱地麦)/南方(水田稻)/西北(400mm 线西·干旱畜牧灌溉)/青藏(一二级阶梯界·高寒河谷农业)；依据=气候+地形；秦淮线=南北界。"),
]

QUESTIONS = [
    ("QB-549", "误差可以消除吗", "物理学", "技术直答",
     ["不能", "减小"], "通识拓展104"),
    ("QB-550", "稀释浓硫酸要注意什么", "化学", "技术直答",
     ["酸入水", "搅拌"], "通识拓展104"),
    ("QB-551", "微生物在食品制作中的应用", "生物学", "技术直答",
     ["酵母", "乳酸菌", "醋"], "通识拓展104"),
    ("QB-552", "中国四大地理区域怎么划分", "地理学", "技术直答",
     ["北方", "南方", "西北", "青藏"], "通识拓展104"),
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
                               "level:L2", "status:verified", "batch:通识拓展104"],
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
    bank["version"] = "v1.96"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
