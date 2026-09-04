# -*- coding: utf-8 -*-
"""seed_common_76_cards.py · 通识拓展批次76知识卡+题库（幂等）

76：物理学-电流的热效应/化学-硬水与软水/生物学-光合作用条件实验/地理学-西气东输
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_jouleheat",
     "电流的热效应：焦耳定律",
     "基础科学知识点内容（人话接口）", "物理学",
     "电流通过导体发热（Q=I²Rt，焦耳定律）——热效应的利用与防范。经典现象：电"
     "炉丝热得发红，跟它串联的导线却不怎么热——电流相同，电炉丝电阻远大于导线"
     "（Q=I²Rt 同流异阻差异悬殊）。发热应用：电炉/电饭锅/电热毯/电烙铁（发热体"
     "用电阻率大的镍铬合金）；防范：导线选电阻率小的铜铝、长时间大功率用电易过"
     "热引发火灾（多重电器同插一个插板是隐患）。电流三大效应：热效应、磁效应"
     "（奥斯特——电流产生磁场）、化学效应（电解）。电热的「双刃剑」对照：保险"
     "丝靠热熔断（fuse 呼应）、电动机却怕发热（效率损失）。",
     ["电炉丝热得发红导线却不热", "什么是焦耳定律", "电流有哪三大效应",
      "电热的应用有哪些", "插板上为什么不能插多个大功率电器", "保险丝熔断原理"],
     ["问焦耳定律计算", "问电动机效率"],
     "atomic", "",
     "焦耳定律 Q=I²Rt：电炉丝红导线不热=同流异阻；发热体用镍铬合金；插板多插大功率=过热火灾隐患；三效应=热/磁(奥斯特)/化学(电解)。"),
    ("kp_card_hardsoft",
     "硬水与软水",
     "基础科学知识点内容（人话接口）", "化学",
     "硬水：含较多可溶性钙、镁化合物的水；软水：不含或含较少。区分方法：加**肥"
     "皂水**搅拌——泡沫多浮渣少=软水；泡沫少浮渣多=硬水（肥皂与钙镁离子反应生"
     "成不溶物）。硬水的危害：①水壶/热水器结水垢（浪费燃料甚至爆炸风险）；②洗"
     "涤效果差（浪费肥皂）；③长期饮用极硬水不利健康（但适量钙镁无害且有益）。"
     "软化方法：生活中**煮沸**（钙镁转化为水垢沉淀析出——水垢就是软化产物）；实"
     "验室/工业**蒸馏**（净化程度最高）。天然水分类：雨水接近软水；海水最硬。矿"
     "泉水≠矿物质越高越好，饮用适口为宜。",
     ["硬水和软水怎么区分", "肥皂水鉴别硬水软水", "怎么软化硬水",
      "水垢是怎么形成的", "煮沸和蒸馏哪个净化程度高", "长期喝硬水有害吗"],
     ["问水垢成分复习", "问离子交换软化"],
     "atomic", "",
     "硬水=多钙镁化合物：肥皂水鉴别(泡沫少浮渣多=硬)；危害=水垢/洗涤差；软化=煮沸(生活·水垢即产物)/蒸馏(最高)；海水最硬·雨水近软。"),
    ("kp_card_photosynthexp",
     "光合作用条件实验：天竺葵遮光",
     "基础科学知识点内容（人话接口）", "生物学",
     "经典实验「绿叶在光下制造有机物」（萨克斯实验）：①暗处理一昼夜——耗尽原"
     "有淀粉（排除干扰）；②叶片部分遮光、部分曝光（**变量=光**，对照实验）；③"
     "光照数小时；④酒精隔水加热脱色（叶绿素溶入酒精，叶片变黄白色——酒精易燃"
     "须隔水）；⑤滴碘液：见光部分变蓝（有淀粉=进行了光合作用），遮光部分不变"
     "蓝——证明：**光是光合作用的必要条件**，产物是淀粉。同类实验：金鱼藻光照"
     "产气泡（氧气——带火星木条复燃证明），证明光合作用释放氧气；诺特用定量方"
     "法证明「植物重建的有机物多于消耗的」。控制变量法是实验设计核心思想。",
     ["怎么证明光合作用需要光", "天竺葵遮光实验", "为什么要暗处理一昼夜",
      "酒精脱色为什么要隔水加热", "滴碘液变蓝说明什么", "什么是对照实验"],
     ["问光合公式总复习", "问氧气检验实验"],
     "atomic", "",
     "萨克斯实验：暗处理耗淀粉→部分遮光(变量=光·对照)→酒精隔水脱色→碘液：见光变蓝=光为必要条件·产物淀粉；金鱼藻气泡=产氧；控制变量法为核心思想。"),
    ("kp_card_westeastgas",
     "西气东输",
     "人文通识知识点内容（人话接口）", "地理学",
     "西气东输：把新疆塔里木盆地等西部的天然气输往东部能源紧缺地区。一线：轮南"
     "（塔里木）→上海，2004 年投产，全长约 4000 公里；二线：霍尔果斯（中亚进口"
     "气+新疆气）→广州，2011 年投产；三线延伸福建。意义：①优化东部能源结构"
     "（天然气替代煤——减少二氧化硫/粉尘，助力蓝天保卫战）；②带动西部经济（塔"
     "里木资源变现）；③管道沿线城市气化。配套概念：西电东送（水电火电南电北送/"
     "西部水电东送三通道）、北煤南运——能源跨区域调配是国情（资源分布与消费地"
     "错位：能源在西部北部、需求在东部南部）。管道安全：管道上方禁挖掘/烧荒，识"
     "别地面标志桩。",
     ["西气东输输送什么", "西气东输一线起点终点", "西气东输的意义",
      "西电东送是什么", "天然气的主要好处", "能源跨区域调配"],
     ["问管道输气原理", "问中俄东线天然气管道"],
     "atomic", "",
     "西气东输：一线=轮南→上海(2004·4000km)/二线=霍尔果斯→广州；意义=东部能源结构优化(气代煤·蓝天)+西部经济带动；配套=西电东送/北煤南运——资源与需求错位的调配。"),
]

QUESTIONS = [
    ("QB-437", "电炉丝热得发红导线却不热", "物理学", "技术直答",
     ["电阻", "焦耳定律"], "通识拓展76"),
    ("QB-438", "硬水和软水怎么区分", "化学", "技术直答",
     ["肥皂水"], "通识拓展76"),
    ("QB-439", "怎么证明光合作用需要光", "生物学", "技术直答",
     ["遮光", "碘液", "淀粉"], "通识拓展76"),
    ("QB-440", "西气东输输送什么", "地理学", "技术直答",
     ["天然气"], "通识拓展76"),
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
                               "level:L2", "status:verified", "batch:通识拓展76"],
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
    bank["version"] = "v1.68"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
