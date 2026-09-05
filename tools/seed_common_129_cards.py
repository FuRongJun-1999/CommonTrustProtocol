# -*- coding: utf-8 -*-
"""seed_common_129_cards.py · 通识拓展批次129知识卡+题库（幂等）

129：物理学-浮力与密度的综合应用/生活常识-家庭小药箱/生物学-转基因食品的利与弊
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_floathollow",
     "浮力与密度的综合应用",
     "基础科学知识点内容（人话接口）", "物理学",
     "用浮力判断物体的空心与实心：比较实际密度与液体密度。例：一个「铁球」放入"
     "水中漂浮——铁密度 7.9g/cm³ 大于水，实心铁球必然下沉，漂浮说明是**空心**"
     "的。三种判断方法（结果一致）：①比较密度（ρ物 vs ρ液）；②比较重力与浮力"
     "（G vs F浮）；③比较 V实（实际铁体积）与 V物（外观体积）。应用：轮船（空心"
     "船体使平均密度小于水）——排水量（排开水的质量）=船自身+货物总质量；潜水"
     "艇靠改变**自身重力**实现浮沉（水舱充水下沉/排水上浮），密度不变改变重"
     "力。气球飞艇：排开空气的浮力>重力时升空。",
     ["怎么判断物体是空心还是实心", "轮船漂浮的原理", "潜水艇怎么实现上浮下潜",
      "排水量是什么意思", "热气球为什么能升空", "浮力的综合应用"],
     ["问浮力计算综合题", "问密度计原理"],
     "atomic", "",
     "空心判断=实心密度应>液体但漂浮→空心；轮船=空心使平均密度<水·排水量=自重+货重；潜水艇=改变自重力浮沉；飞艇=排空气浮力>重力。"),
    ("kp_card_homekit",
     "家庭小药箱：常备药品",
     "生活常识知识点内容（人话接口）", "生活常识",
     "家庭小药箱常备清单：①**退烧止痛**——布洛芬/对乙酰氨基酚（二选一，不叠加"
     "——同时服过量伤肝）；②**外伤处理**——碘伏（消毒不痛）、创可贴、无菌纱布"
     "/绷带、医用胶带；③**消化**——口服补液盐（腹泻脱水）、蒙脱石散（止泻）、"
     "健胃消食片；④**抗过敏**——氯雷他定（荨麻疹/过敏性鼻炎）；⑤**工具**——体"
     "温计、剪刀、镊子、一次性手套。管理要点：避光阴凉干燥保存（部分需冷藏）、"
     "每 3-6 个月检查效期（过期药交至药店回收点——不可随意丢弃污染环境）、儿"
     "童药单独存放防误食。处方药需医生开具，不自行囤积使用。",
     ["家庭小药箱常备什么药", "退烧药有哪些", "碘伏和酒精消毒的区别",
      "过期药怎么处理", "儿童用药注意事项", "布洛芬和对乙酰氨基酚的区别"],
     ["问常见用药误区", "问儿童禁用药物清单"],
     "atomic", "",
     "家庭药箱常备=布洛芬或对乙酰氨基酚退烧(二选一不叠加)+碘伏创可贴+补液盐+氯雷他定+体温计；管理=避光干燥·3-6 月查效期·过期交药店回收。"),
    ("kp_card_gmo",
     "转基因食品的利与弊",
     "基础科学知识点内容（人话接口）", "生物学",
     "转基因食品：通过基因工程技术将外源基因导入生物体获得的食品。**利**：①增"
     "产抗逆（转 Bt 基因抗虫棉减少农药使用 80%+、耐旱耐盐碱品种）；②提升营养（"
     "黄金大米转 β-胡萝卜素合成基因——对抗维生素 A 缺乏致盲）；③减少农药残留"
     "（抗虫少喷药）。**争议与风险**：①生态环境（基因漂移到野生近缘种产生「超级"
     "杂草」）；②过敏风险（新蛋白可能致敏——需严格安全评价）；③伦理（自然性/"
     "巨头垄断种子专利）。中国政策：转基因成分>0.9% 须标识、批准上市的转基因"
     "食品（木瓜/棉籽油等）经过严格安全评价——至今无确证安全问题的案例。科学"
     "共识：已批准上市的转基因食品与传统食品「实质等同」同样安全。",
     ["转基因食品的利与弊", "转基因食品安全吗", "抗虫棉的原理",
      "黄金大米是什么", "转基因食品要标识吗", "什么是实质等同原则"],
     ["问基因漂移研究", "问全球转基因种植面积"],
     "atomic", "",
     "转基因利=抗虫(棉 Bt 减农药 80%)+营养(黄金大米 β-胡萝卜素)+抗逆；争议=基因漂移+致敏风险+种子专利；中国>0.9% 须标识；已批准上市=实质等同安全·无确证案例。"),
]

QUESTIONS = [
    ("QB-653", "怎么判断物体是空心还是实心", "物理学", "技术直答",
     ["密度", "漂浮"], "通识拓展129"),
    ("QB-654", "家庭小药箱常备什么药", "生活常识", "技术直答",
     ["退烧药", "碘伏", "创可贴"], "通识拓展129"),
    ("QB-655", "转基因食品的利与弊", "生物学", "技术直答",
     ["增产", "抗虫", "争议"], "通识拓展129"),
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
                               "level:L2", "status:verified", "batch:通识拓展129"],
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
    bank["version"] = "v4.1"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
