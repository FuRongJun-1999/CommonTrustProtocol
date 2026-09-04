# -*- coding: utf-8 -*-
"""seed_common_62_cards.py · 通识拓展批次62知识卡+题库（幂等）

62：物理学-电磁波家族/化学-水的三态变化/生物学-光合与呼吸的关系/地理学-珊瑚岛
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_emwave",
     "电磁波家族",
     "基础科学知识点内容（人话接口）", "物理学",
     "电磁波以光速传播（3×10⁸ m/s），不需要介质（可在真空中传播——与声波本质区"
     "别）。按波长/频率排成电磁波谱：无线电波（广播/手机/WiFi——微波也是无线电"
     "波，微波炉加热水分子）→红外线（遥控器/热成像/取暖）→可见光（红橙黄绿蓝靛"
     "紫，人眼能看见的窄段）→紫外线（杀菌/验钞/晒黑）→X 射线（医学透视/机场安"
     "检）→γ 射线（核辐射，穿透最强）。频率越高、波长越短、能量越大（紫外线以上"
     "过量伤身）。手机通信靠无线电波（微波段）；光纤通信其实用激光（光也是电磁"
     "波）。5G 用更高频段——速度更快但绕射弱、基站更密。电磁污染：规范内安全，"
     "但别贴着路由器长时间睡。",
     ["手机通信靠什么传递信息", "电磁波包括哪些", "微波炉用什么波加热",
      "红外线和紫外线的应用", "电磁波需要介质吗", "5G为什么基站更密"],
     ["问麦克斯韦电磁理论", "问光谱分析复习"],
     "atomic", "",
     "电磁波谱=无线电(手机/WiFi/微波炉)→红外(遥控热成像)→可见光→紫外(杀菌验钞)→X 光→γ；真空中光速传播不需介质；频率高波长短能量大；5G 高频基站密。"),
    ("kp_card_w3states",
     "水的三态变化",
     "基础科学知识点内容（人话接口）", "化学",
     "水的三种状态（冰/水/水蒸气）之间的六种变化：熔化（冰→水，吸热）、凝固"
     "（水→冰，放热）、汽化（水→水蒸气，吸热：蒸发+沸腾两种方式）、液化（水蒸"
     "气→水，放热：白气/露水/雾）、升华（冰直接→水蒸气，吸热：冬天冻衣服变干/"
     "樟脑丸变小）、凝华（水蒸气直接→冰，放热：霜/雪/窗花/雾凇）。规律：熔化汽"
     "化升华吸热，凝固液化凝华放热（记「三吸三放」）。零摄氏度的冰与水，冰的内能"
     "更小（晶体熔化吸热温度不变——能量藏在分子势能里）。舞台「干冰造雾」：干冰"
     "升华吸热使空气中水蒸气液化成小水珠（雾是液滴不是 CO₂）。",
     ["水蒸气变成水是什么变化", "六种物态变化", "霜和雪是怎么形成的",
      "冬天冻衣服为什么能干", "干冰造雾的原理", "哪些物态变化放热"],
     ["问晶体非晶体熔化曲线", "问人工降雨流程"],
     "atomic", "",
     "六变三吸(熔化/汽化/升华)三放(凝固/液化/凝华)：白气露雾=液化·霜雪窗花=凝华·冻衣干=升华(吸热)；0℃ 冰内能<水；干冰雾=CO₂升华吸热→水汽液化。"),
    ("kp_card_photoresp",
     "光合作用与呼吸作用的关系",
     "基础科学知识点内容（人话接口）", "生物学",
     "光合作用（白天，叶绿体）：二氧化碳+水→有机物+氧气，储**存**能量；呼吸作用"
     "（昼夜不停，所有活细胞线粒体）：有机物+氧气→二氧化碳+水+能量，**释放**能"
     "量供生命活动——两者互为逆过程但不是简单的可逆反应（场所/条件/意义都不同）。"
     "常见误区：植物白天只放氧气不放二氧化碳？——错，白天光合远强于呼吸（净放"
     "氧），晚上只呼吸（净耗氧）。「卧室放很多植物晚上抢氧气」有一定道理但量微"
     "小。农业应用：合理密植（充分利用光照）、温室补充 CO₂（气肥）增产、夜晚适"
     "当降温减少呼吸消耗（温室瓜果更甜的原理——昼夜温差大糖分积累多，如新疆瓜"
     "果甜）。",
     ["植物晚上会放出氧气吗", "光合作用和呼吸作用的区别", "呼吸作用的场所",
      "为什么新疆瓜果特别甜", "什么是合理密植", "温室气肥是什么"],
     ["问光合呼吸曲线题", "问粮食储存低温低氧"],
     "atomic", "",
     "光合(白天·叶绿体·储能 CO₂+H₂O→有机物+O₂)vs 呼吸(昼夜·线粒体·释能)互逆非可逆；白天净放氧/夜间净耗氧(量微)；应用=密植/气肥/昼夜温差大瓜果甜。"),
    ("kp_card_coralisle",
     "珊瑚岛与珊瑚礁",
     "人文通识知识点内容（人话接口）", "地理学",
     "珊瑚岛由珊瑚虫的石灰质骨骼堆积而成：珊瑚虫是腔肠动物，固定在浅海海底、只"
     "能生活在水温 20℃ 以上、光照充足（共生虫黄藻需要光合）的清澈浅海——所以珊"
     "瑚礁几乎都在热带海洋。类型演变：岸礁（贴岸）→堡礁（离岸，澳洲大堡礁全长"
     "约 2300 公里为世界最大）→环礁（中间泻湖，如南海诸岛多为环礁）——地壳缓慢"
     "下沉+珊瑚向上生长的经典模型（达尔文提出）。南海诸岛（西沙/南沙/中沙）多为"
     "珊瑚岛礁，是重要海洋国土；三沙市管辖。生态警报：海水升温导致珊瑚白化（虫"
     "黄藻离开，珊瑚失去颜色与主要能量来源而死亡）——全球变暖的直观指标。珊瑚"
     "是动物不是植物/石头（会动、捕食浮游生物）。",
     ["珊瑚岛是怎么形成的", "大堡礁在哪里", "珊瑚是动物还是植物",
      "珊瑚白化是怎么回事", "南海诸岛是什么岛", "什么是环礁"],
     ["问共生关系复习", "问海洋酸化"],
     "atomic", "",
     "珊瑚岛=珊瑚虫(腔肠动物·非植物)骨骼堆积：岸礁→堡礁(大堡礁 2300km 最大)→环礁(南海多为环礁)；条件=热带浅海清澈(共生虫黄藻)；白化=升温排藻·全球变暖指标。"),
]

QUESTIONS = [
    ("QB-381", "手机通信靠什么传递信息", "物理学", "技术直答",
     ["电磁波"], "通识拓展62"),
    ("QB-382", "水蒸气变成水是什么变化", "化学", "技术直答",
     ["液化"], "通识拓展62"),
    ("QB-383", "植物晚上会放出氧气吗", "生物学", "技术直答",
     ["不会", "呼吸作用"], "通识拓展62"),
    ("QB-384", "珊瑚岛是怎么形成的", "地理学", "技术直答",
     ["珊瑚虫", "骨骼堆积"], "通识拓展62"),
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
                               "level:L2", "status:verified", "batch:通识拓展62"],
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
    bank["version"] = "v1.54"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
