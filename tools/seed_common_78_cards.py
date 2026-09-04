# -*- coding: utf-8 -*-
"""seed_common_78_cards.py · 通识拓展批次78知识卡+题库（幂等）

78：物理学-能源的分类/化学-金属活动性置换/生物学-光合作用的意义/地理学-地球的形状
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞——本批预检命中
kp_card_foodchain（夜间v0.2旧卡·食物链已覆盖），生物题改光合作用的意义。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_energyclass",
     "能源的分类",
     "基础科学知识点内容（人话接口）", "物理学",
     "能源多维度分类：①按能否再生——可再生能源（太阳能/风能/水能/生物质能/地热"
     "能/潮汐能）与不可再生能源（煤/石油/天然气/核燃料）；②按是否直接来自自然"
     "——一次能源（煤/石油/天然气/风/光——直接取自自然）与二次能源（电能/汽油"
     "/焦炭/酒精——由一次能源加工转换而来）；③按是否常规——常规能源（煤/油气"
     "/水能）与新能源（太阳能/风能/核能/地热/氢能/可燃冰）。易错点：电能是二次"
     "能源（不是一次能源）；核能是不可再生能源（核燃料有限）；「无污染」是相对的"
     "——电池生产与处置也有环境代价。人类能源史：柴薪→煤炭（蒸汽时代）→石油"
     "（内燃机时代）→多元化（核/再生能源时代）。",
     ["可再生能源和不可再生能源", "电能是一次能源吗", "什么是新能源",
      "一次能源和二次能源的区别", "人类能源史的三个阶段", "核能可再生吗"],
     ["问能源结构转型数据", "问能源安全战略"],
     "atomic", "",
     "能源分类：可再生(风光水生物质地热潮汐)vs 不可再生(化石+核燃料)；一次(直接取自自然)vs 二次(电/汽油/酒精)；核能=不可再生；新能源=风光核地热氢可燃冰。"),
    ("kp_card_displace",
     "金属活动性与置换反应",
     "基础科学知识点内容（人话接口）", "化学",
     "金属活动性顺序（K Ca Na Mg Al Zn Fe Sn Pb (H) Cu Hg Ag Pt Au）——排前"
     "面的金属更活泼，能把排后面的金属从其盐溶液中**置换**出来：铁钉放入硫酸铜溶"
     "液，表面覆盖红色铜、溶液变浅绿（Fe + CuSO₄ → FeSO₄ + Cu）——所以铁桶不"
     "能装硫酸铜溶液（会腐蚀且溶液报废）。判断规则：①排在氢前的金属能与稀盐酸/"
     "稀硫酸反应放出氢气（铜银不反应——实验室制氢气用锌不选镁太快的经济性）；②"
     "排前面的置换排后面的；③钾钙钠太活泼，入水先与水剧烈反应（放水中不能置换盐"
     "中金属）。置换反应定义：单质+化合物→新单质+新化合物（A+BC→AC+B）。",
     ["为什么铁桶不能装硫酸铜溶液", "金属活动性顺序表", "什么是置换反应",
      "哪些金属能与稀盐酸反应", "实验室制氢气为什么用锌", "铁和硫酸铜反应现象"],
     ["问湿法炼铜（曾青得铁）", "问活动性实验设计"],
     "atomic", "",
     "活动序 K…(H)…Au：前排置换后排（铁+硫酸铜→铜析出·溶液变浅绿→铁桶忌装）；氢前金属+稀酸放氢(制氢用锌)；钾钙钠先与水反应；置换=单质+化合物→新单质+新化合物。"),
    ("kp_card_photomean",
     "光合作用的意义",
     "基础科学知识点内容（人话接口）", "生物学",
     "光合作用是地球上最重要的化学反应之一，三大意义：①**食物来源**——把无机物"
     "合成有机物，养活地球上几乎全部生物（食物链的起点；人类粮食能源本质都是「当"
     "代或古代的光合产物」——煤石油是亿万年前的光合储蓄）；②**能量来源**——把"
     "光能转化为化学能储存在有机物中（每年固定的太阳能约为人类年能耗的 10 倍）；"
     "③**维持大气氧碳平衡**——释放氧气、吸收二氧化碳（海洋藻类贡献约一半的产"
     "氧）。公式：二氧化碳+水 →（光能/叶绿体）有机物+氧气。光合作用还「改造」了"
     "地球：约 24 亿年前蓝藻的光合作用制造了大氧化事件，为需氧生命（包括人类）铺"
     "路。",
     ["光合作用有什么意义", "食物链的能量从哪来", "煤和石油的本质是什么",
      "大气中的氧气从哪里来", "光合作用反应式", "大氧化事件"],
     ["问呼吸作用对比总复习", "问叶绿体结构"],
     "atomic", "",
     "光合三大意义=食物来源(食物链起点·化石燃料是古代光合储蓄)+能量来源(光→化学能·年固定≈人类 10 倍能耗)+氧碳平衡(藻类产半数氧·大氧化事件铺路)。"),
    ("kp_card_earthshape",
     "地球的形状与大小",
     "人文通识知识点内容（人话接口）", "地理学",
     "地球是一个**两极稍扁、赤道略鼓的不规则球体**——不是完美正球体（自转离心"
     "力使赤道鼓出）。认识历程：天圆地方→据月食影子/帆船远近推测球体→1519-1522"
     " 年麦哲伦船队环球航行（人类首次实证）→现代卫星测量精确形状。数据：平均半"
     "径约 6371 千米，赤道周长约 4 万千米（「坐地日行八万里」指赤道自转——8 万"
     "里=4 万公里），表面积约 5.1 亿平方公里（71% 海洋 29% 陆地）。人类首次看到"
     "地球全貌：1968 年阿波罗 8 号「地出」照片——被称为「蓝色弹珠」，催生环保意"
     "识。证据链：月食地球影子是圆弧、不同纬度北极星高度不同、环球航行、卫星照"
     "片。",
     ["地球的真实形状是什么", "地球的平均半径", "谁第一次证明地球是球体",
      "坐地日行八万里什么意思", "地球表面海陆比例", "地出照片"],
     ["问经纬网定位复习", "问人类宇宙观演变"],
     "atomic", "",
     "地球=两极稍扁赤道略鼓不规则球体(自转离心)；半径 6371km·赤道周长 4 万km(坐地日行八万里)·71% 海；实证=麦哲伦环球(1519-22)；「地出」照催生环保意识。"),
]

QUESTIONS = [
    ("QB-445", "电能是一次能源吗", "物理学", "技术直答",
     ["不是", "二次能源"], "通识拓展78"),
    ("QB-446", "为什么铁桶不能装硫酸铜溶液", "化学", "技术直答",
     ["置换", "腐蚀"], "通识拓展78"),
    ("QB-447", "光合作用有什么意义", "生物学", "技术直答",
     ["食物", "能量", "氧气"], "通识拓展78"),
    ("QB-448", "地球的真实形状是什么", "地理学", "技术直答",
     ["两极稍扁", "赤道略鼓", "不规则球体"], "通识拓展78"),
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
                               "level:L2", "status:verified", "batch:通识拓展78"],
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
    bank["version"] = "v1.70"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
