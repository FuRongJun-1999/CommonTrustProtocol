# -*- coding: utf-8 -*-
"""seed_common_128_cards.py · 通识拓展批次128知识卡+题库（幂等）

128：物理学-多普勒效应/化学-食品中的化学知识/生物学-生态系统的自我调节/地理学-中国的气候类型
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_doppler",
     "多普勒效应",
     "基础科学知识点内容（人话接口）", "物理学",
     "多普勒效应：当波源与观察者有相对运动时，观察者接收到的**频率**发生变化的"
     "现象。①靠近——频率变高（音调变高）；②远离——频率变低（音调变低）。经典"
     "例子：救护车鸣笛驶来时音调变高、驶离时变低。应用：①**雷达测速**——交警测"
     "车速（反射波频率变化计算车速）；②医学超声（多普勒彩超测血流速度方向）；③"
     "天文学——红移（星系远离我们，光谱向红端偏移）证明宇宙膨胀（哈勃定律）；④"
     "气象雷达（测云层移动）。1842 年多普勒提出，声光电磁波均适用。",
     ["什么是多普勒效应", "救护车靠近时音调为什么变高", "雷达测速的原理",
      "多普勒彩超是什么", "宇宙膨胀的证据", "红移是什么"],
     ["问哈勃定律", "问多普勒效应公式"],
     "atomic", "",
     "多普勒效应=波源与观察者相对运动致频率变化：靠近变高·远离变低；应用=雷达测速/多普勒彩超/红移证宇宙膨胀(哈勃)；声光电磁均适用。"),
    ("kp_card_chemfood",
     "食品中的化学知识",
     "基础科学知识点内容（人话接口）", "化学",
     "食品中的化学知识无处不在：①**烘焙**——小苏打受热分解产 CO₂ 使面点蓬松；"
     "②**防腐**——盐腌（渗透压脱水抑菌）、糖渍（高糖环境抑菌——蜜饯）、醋酸"
     "（酸环境抑菌——泡菜）；③**变色**——苹果切开变褐（酚类氧化，柠檬汁 VC 抗"
     "氧化防变色）、绿茶变红（茶多酚氧化）；④**味觉化学**——味精（谷氨酸钠）鲜"
     "味、食盐咸味、糖甜味；⑤**烹饪**——铁锅补铁（少量铁离子溶出）、煮饺子加点"
     "盐不易破（渗透压）、焯水去草酸（菠菜豆腐同炒更科学）；⑥**油脂酸败**——油"
     "放久了哈喇味（氧化分解），避光密封保存。",
     ["食品中的化学知识有哪些", "为什么煮饺子加盐不易破", "苹果切开后为什么变色",
      "味精的化学成分", "油脂为什么会变哈喇味", "小苏打发酵的原理"],
     ["问食品添加剂安全复习", "问美拉德反应"],
     "atomic", "",
     "食品化学=烘焙小苏打产气+盐腌糖渍抑菌+苹果变褐酚氧化(柠檬VC抗)+味精谷氨酸钠+煮饺子盐渗透压+油脂氧化哈喇味——避光密封保存。"),
    ("kp_card_ecoregulate",
     "生态系统的自我调节能力",
     "基础科学知识点内容（人话接口）", "生物学",
     "生态系统具有**自我调节能力**：通过负反馈调节使各种生物数量保持相对稳定——"
     "例：兔多→草少→兔饿死减少→草恢复→兔增多→草又减少……循环制约。规律：①"
     "**生物种类越多、营养结构越复杂**，自我调节能力越强（热带雨林>草原>荒漠）"
     "；②调节能力有**限度**——超过限度（大火/污染/大规模砍伐）生态平衡就被破"
     "坏。人类活动影响：过度开发打破平衡（过度放牧→草原退化）、外来物种入侵"
     "（水葫芦堵塞河道）、环境污染（富营养化→水华）。保护：退耕还林、建立自然"
     "保护区、控制污染排放。生态平衡是动态平衡而非静止不变。",
     ["生态系统的自我调节能力", "为什么热带雨林生态系统最稳定",
      "生态平衡是绝对不变的吗", "生态系统的调节能力有限度吗",
      "负反馈调节是什么", "怎样保护生态平衡"],
     ["问生态承载力", "问生态恢复工程"],
     "atomic", "",
     "自我调节=负反馈维持相对稳定(兔草循环)：种类越多结构越复杂调节越强(雨林>草原>荒漠)；**有限度**超限破坏不可逆；保护=自然保护区+控污+可持续。"),
    ("kp_card_chinaclimatetype",
     "中国的气候类型",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国气候类型复杂多样，主要有五种：①**热带季风气候**——海南/云南南部/台"
     "湾南部：全年高温、分旱雨两季；②**亚热带季风气候**——秦岭淮河以南：夏热"
     "多雨冬温和少雨（江南/华南/川渝）；③**温带季风气候**——秦岭淮河以北：夏"
     "热多雨冬寒冷干燥（华北/东北）；④**温带大陆性气候**——西北内陆：干旱少"
     "雨、温差大（新疆/内蒙古/甘肃）；⑤**高原山地气候**——青藏高原：高寒、垂"
     "直变化明显（「一山有四季，十里不同天」）。成因：海陆热力差异（季风）+纬"
     "度+地形。中国气候三大特征：季风气候显著、气候复杂多样、雨热同期。",
     ["中国的气候类型有哪些", "中国的五种气候类型", "什么是高原山地气候",
      "温带季风气候的特点", "中国气候的三大特征", "雨热同期是什么意思"],
     ["问季风成因详解", "问气候与农业分布"],
     "atomic", "",
     "中国五气候=热带季风(海南)+亚热带季风(南方)+温带季风(北方)+温带大陆性(西北)+高原山地(青藏)；特征=季风显著+复杂多样+雨热同期；成因=海陆差异+纬度+地形。"),
]

QUESTIONS = [
    ("QB-647", "什么是多普勒效应", "物理学", "技术直答",
     ["频率变化", "相对运动"], "通识拓展128"),
    ("QB-648", "食品中的化学知识有哪些", "化学", "技术直答",
     ["防腐", "变色", "烘焙"], "通识拓展128"),
    ("QB-649", "生态系统的自我调节能力", "生物学", "技术直答",
     ["负反馈", "有限度"], "通识拓展128"),
    ("QB-650", "中国的气候类型有哪些", "地理学", "技术直答",
     ["热带季风", "亚热带季风", "温带季风", "温带大陆性", "高原山地"], "通识拓展128"),
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
                               "level:L2", "status:verified", "batch:通识拓展128"],
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
    bank["version"] = "v4.2"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
