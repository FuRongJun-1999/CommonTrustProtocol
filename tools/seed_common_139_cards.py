# -*- coding: utf-8 -*-
"""seed_common_139_cards.py · 通识拓展批次139知识卡+题库（幂等）

139：生活常识-高铁动车乘车常识/化学-玻璃与陶瓷/物理-保温杯与热传递阻断
KCCS 四要素+题干原句触发词。三重预检：transport=交通史卡（乘车实务未覆盖）、
玻璃卡=高分子玻璃态（材料工艺未覆盖）、保温杯双库零覆盖（真空/热传递卡为原
理角度，本卡为应用角度互补）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hsrtravel",
     "高铁动车乘车常识",
     "生活常识知识点内容（人话接口）", "生活常识",
     "车次字母含义：**G=高铁**（时速 300-350km，武汉-广州等干线）、**D=动车**"
     "（200-250km，车型 CRH/CR 动车组）、C=城际铁路（相邻城市间短途）。乘车流"
     "程：**实名制购票**（12306 App/车站，一证一票）→电子客票无需取票、身份"
     "证刷闸进站→安检（易燃易爆/管制刀具禁带；**充电宝≤100Wh 且必须随身携"
     "带、不得托运**；酒精等易燃液体禁带）→候车（大站开车前通常提前 5 分钟停"
     "止检票，勿卡点）→按车厢号候车牌对应位置排队。儿童票 2023 新规按年龄：6"
     " 周岁前免票（不占座）、6-14 周岁半价、14 周岁以上全价。车上禁止吸烟"
     "（含电子烟，触发烟雾报警罚款并列入失信名单）。",
     ["高铁和动车有什么区别", "G字头D字头是什么意思", "坐高铁需要取票吗",
      "高铁充电宝能带吗", "儿童高铁票怎么收费", "高铁上能抽烟吗"],
     ["问具体线路时刻票价", "问改签退票手续费标准"],
     "atomic", "",
     "G=高铁 300-350km/h、D=动车 200-250、C=城际；电子客票身份证刷闸不需取票；充电宝≤100Wh 必须随身禁托运；管制刀具易燃易爆禁带；大站开车前 5 分钟停检；儿童票按年龄 6 免 6-14 半 14 全；车上吸烟触发报警罚+失信。"),
    ("kp_card_glassceramic",
     "玻璃与陶瓷",
     "基础科学知识点内容（人话接口）", "化学",
     "玻璃：原料=石英砂（SiO₂）+纯碱+石灰石高温熔融——**无定形非晶体**（原子"
     "排列无序，没有固定熔点，受热逐渐软化，故可吹制/拉制各种形状）；普通玻璃"
     "为钠钙玻璃；**钢化玻璃**=普通玻璃加热后急冷淬火，表面压应力使其强度提"
     "高 4-5 倍，破碎时呈钝角小颗粒不易伤人（汽车侧窗/手机贴膜同类思路）；磨"
     "砂玻璃=表面粗糙使光漫反射。氢氟酸能腐蚀玻璃（雕花玻璃工艺）——盛氢氟酸"
     "不用玻璃瓶。陶瓷：黏土（含高岭土）成型后**高温烧制**——陶器（约 1000°C，"
     "多孔吸水，常施釉）→瓷器（**1200°C 以上**，胎体致密白亮敲之清脆）；英文"
     "「china」小写即瓷器——瓷器是中国伟大发明，宋代五大名窑（汝官哥钧定）。"
     "水泥/玻璃/陶瓷并称三大传统硅酸盐材料。",
     ["玻璃是晶体吗", "钢化玻璃为什么安全", "陶瓷和瓷器有什么区别",
      "为什么氢氟酸能刻玻璃", "china瓷器由来", "玻璃的原料是什么"],
     ["问玻璃回收分类", "问建筑幕墙安全"],
     "atomic", "",
     "玻璃=石英砂+纯碱+石灰石熔融，无定形非晶体无固定熔点可吹制；钢化=淬火增压碎成钝粒；氢氟酸蚀刻玻璃故不能玻璃瓶装；陶器 1000°C 多孔上釉/瓷器 1200°C+ 致密白亮（china 小写=瓷器，宋代五大名窑汝官哥钧定）；水泥玻璃陶瓷=三大硅酸盐。"),
    ("kp_card_thermos",
     "保温杯为什么保温",
     "基础科学知识点内容（人话接口）", "物理学",
     "热传递有三种方式：**传导**（接触传热）、**对流**（流体流动带热）、**辐"
     "射**（电磁波传热）。保温杯（杜瓦瓶原理）对三种方式各断一环：①**真空夹"
     "层**——双层不锈钢壁间抽成真空，真空不传热，切断**传导**和**对流**（没"
     "有介质）；②**内壁镀银/镀铜**——像镜子一样把热辐射反射回去，切断**辐"
     "射**；③**密封杯盖**——堵住最上方的对流通道。所以保温杯既能保热也能保"
     "冷（阻断的是双向热传递：热水凉得慢、冰水化得慢）。使用注意：装过热开水"
     "别拧太满（气压顶开塞喷溅）；不能装碳酸饮料/干冰（气体膨胀顶盖）；奶类"
     "久放杯中易变质酸败。",
     ["保温杯的原理", "真空层为什么能保温", "热传递三种方式",
      "保温杯为什么能保冷", "保温杯不能装什么", "镀银是为了防什么传热"],
     ["问保温杯品牌选购", "问电热水壶原理（电热转换）"],
     "atomic", "",
     "热传递三方式=传导/对流/辐射；保温杯=真空夹层断传导+对流（无介质）+内壁镀银反射辐射+杯盖堵对流，双向阻断故亦保冷；禁装碳酸饮料/干冰（胀顶）与久放奶类（酸败）。"),
]

QUESTIONS = [
    ("QB-681", "高铁车次开头的字母 G 和 D 分别代表什么？坐高铁需要取纸质票吗？", "生活常识", "技术直答",
     ["高铁", "动车", "G", "D", "电子客票", "刷身份证"], "通识拓展139"),
    ("QB-682", "玻璃是晶体吗？钢化玻璃为什么破碎后不容易伤人？", "化学", "技术直答",
     ["不是", "非晶体", "无定形", "钝角", "颗粒", "淬火"], "通识拓展139"),
    ("QB-683", "保温杯的真空夹层主要阻断了哪几种热传递方式？内壁镀银又是为了什么？", "物理学", "技术直答",
     ["传导", "对流", "真空", "辐射", "反射"], "通识拓展139"),
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
                               "level:L2", "status:verified", "batch:通识拓展139"],
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
    bank["version"] = "v4.12"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
