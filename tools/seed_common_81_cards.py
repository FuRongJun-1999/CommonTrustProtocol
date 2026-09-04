# -*- coding: utf-8 -*-
"""seed_common_81_cards.py · 通识拓展批次81知识卡+题库（幂等）

81：物理学-增大与减小压强/化学-有机物与无机物/生物学-花的结构/地理学-中国工业分布
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_pressapp",
     "增大与减小压强的方法",
     "基础科学知识点内容（人话接口）", "物理学",
     "压强 p=F/S（压力÷受力面积）——增大或减小压强就是调控压力与受力面积：**增"
     "大压强**——①压力一定减小受力面积：刀刃磨薄、针尖做尖、破窗锤锥头；②受"
     "力面积一定增大压力：用力按图钉。**减小压强**——①压力一定增大受力面积：书"
     "包带宽背带、坦克履带、铁轨下铺枕木、骆驼宽脚掌、滑雪板；②受力面积一定减"
     "小压力：限量载重（桥梁限重）。生活例子丰富：菜刀（磨刃=增大）、图钉/缝衣"
     "针（尖=增大）、骆驼/滑雪板/履带（宽=减小）、骆驼刺根系。p 的单位帕斯卡"
     "（Pa=1N/m²）——一张报纸平放对桌面的压强约 0.5Pa。",
     ["增大和减小压强的方法", "书包带为什么做宽", "刀刃为什么要磨得锋利",
      "坦克为什么装履带", "压强的公式和单位", "铁轨下为什么铺枕木"],
     ["问柱体压强推导", "问生活压强现象归类"],
     "atomic", "",
     "压强 p=F/S：增大=减面积(刀刃针尖)或增压力；减小=增面积(宽书包带/履带/枕木/滑雪板)或减压；Pa=N/m²；「磨刀不误砍柴工」=增大压强提效。"),
    ("kp_card_organic",
     "有机物与无机物",
     "基础科学知识点内容（人话接口）", "化学",
     "有机物（有机化合物）：含碳的化合物（除 CO、CO₂、碳酸、碳酸盐等——它们的"
     "性质与无机物相近，归无机）。特点：多数难溶于水、易燃、熔点低、种类极多"
     "（数千万种，远超无机物——碳原子可连成长链/环状）。最大家族：烃（碳氢化合"
     "物——甲烷/丁烷/汽油成分）及其衍生物（乙醇/乙酸/糖类/蛋白质/塑料橡胶纤"
     "维）。无机物：不含碳的化合物+少数含碳化合物（水/食盐/盐酸/烧碱/硫酸/碳"
     "酸盐等），种类约十几万。尿素（CO(NH₂)₂）本是第一个人工合成的有机物（1828"
     " 年维勒——打破「有机物只能来自生命体」的「生命力论」）。有机物与生活：食"
     "物三大产能营养素（糖类/脂肪/蛋白质）、维生素都是有机物。",
     ["甲烷是有机物吗", "什么是有机物", "CO₂是有机物吗", "有机物和无机物怎么区分",
      "第一个人工合成的有机物", "有机物有什么特点"],
     ["问有机物命名系统", "问高分子化合物"],
     "atomic", "",
     "有机物=含碳化合物(除 CO/CO₂/碳酸盐)：多数难溶易燃熔低·数千万种(碳可成链成环)；尿素=维勒 1828 首合破生命力论；三大产能营养素皆有机。"),
    ("kp_card_flowerstr",
     "花的结构：雄蕊与雌蕊是主角",
     "基础科学知识点内容（人话接口）", "生物学",
     "一朵完全花包括：花萼（外层保护瓣）、花冠（花瓣，吸引传粉者）、雄蕊、雌蕊"
     "——**雄蕊和雌蕊（合称花蕊）是花的主要结构**，因为它们与果实和种子的形成直"
     "接相关。雄蕊=花丝+花药（花药里有花粉——内含精子）；雌蕊=柱头（接受花"
     "粉）+花柱+**子房**（内有胚珠——受精后发育成种子，子房发育成果实）。传粉方"
     "式：自花传粉（豌豆）/异花传粉（虫媒花——鲜艳芳香有蜜；风媒花——花粉多而"
     "轻，如玉米杨柳）。人工授粉：为弥补自然传粉不足，向日葵/瓜类常用——「缺苗"
     "断垄颗粒稀」的应对。单性花 vs 两性花：黄瓜南瓜是单性花（雌雄同株异花，雄"
     "花不结果）。",
     ["一朵花的主要结构是什么", "雄蕊和雌蕊的组成", "子房发育成什么",
      "虫媒花和风媒花的区别", "为什么要人工授粉", "黄瓜的雄花能结果吗"],
     ["问受精双受精过程", "问花与果实对应关系"],
     "atomic", "",
     "花主结构=雄蕊(花丝+花药含花粉)与雌蕊(柱头+花柱+子房含胚珠)：受精后子房→果实·胚珠→种子；虫媒花艳香蜜/风媒花粉多而轻；黄瓜南瓜=单性花异花。"),
    ("kp_card_industry",
     "中国工业的分布",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国工业分布特点：**沿海、沿江、沿铁路线**布局（交通便利+市场+劳动力集"
     "中）。四大工业基地（都在东部沿海，自北向南）：①辽中南——重工业基地（鞍"
     "山钢铁/大连造船，资源型老基地）；②京津唐——北方最大综合性工业基地（科"
     "技+资源+交通）；③沪宁杭（长江三角洲）——全国最大综合性工业基地（市场广"
     "阔/水陆运输/技术资金雄厚，缺资源能源靠输入）；④珠江三角洲——以轻工业为主"
     "的出口加工基地（毗邻港澳·外资）。新兴趋势：中西部承接产业转移（重庆笔电基"
     "地）、高科技产业（北京中关村——中国「硅谷」）。工业区位因素：资源、交通、"
     "市场、劳动力、技术、政策。",
     ["中国工业分布的特点", "四大工业基地是哪四个", "沪宁杭工业基地",
      "中关村是干什么的", "辽中南工业基地的特点", "工业布局考虑哪些因素"],
     ["问工业基地对比表", "问产业转移趋势"],
     "atomic", "",
     "中国工业=沿海沿江沿铁路；四基地自北南：辽中南(重工业)/京津唐(北方综合)/沪宁杭(最大综合·缺资源)/珠三角(轻工业出口)；新兴=中西部转移+中关村科创。"),
]

QUESTIONS = [
    ("QB-457", "增大和减小压强的方法", "物理学", "技术直答",
     ["受力面积", "压力"], "通识拓展81"),
    ("QB-458", "甲烷是有机物吗", "化学", "技术直答",
     ["是", "含碳"], "通识拓展81"),
    ("QB-459", "一朵花的主要结构是什么", "生物学", "技术直答",
     ["雄蕊", "雌蕊"], "通识拓展81"),
    ("QB-460", "中国工业分布的特点", "地理学", "技术直答",
     ["沿海", "沿江", "沿铁路"], "通识拓展81"),
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
                               "level:L2", "status:verified", "batch:通识拓展81"],
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
    bank["version"] = "v1.73"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
