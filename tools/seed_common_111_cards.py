# -*- coding: utf-8 -*-
"""seed_common_111_cards.py · 通识拓展批次111知识卡+题库（幂等）

111：物理学-密度的测量排水法/化学-二氧化碳与一氧化碳对比/生物学-细菌真菌在自然界中的作用
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_densitymeasure",
     "测量不规则物体的密度（排水法）",
     "基础科学知识点内容（人话接口）", "物理学",
     "测不规则固体（如小石块）密度的方法：①用托盘天平测质量 m；②量筒装适量"
     "水读体积 V₁；③用细线拴住石块**缓慢浸没**入量筒读总体积 V₂；④石块体积="
     "V₂−V₁（排水法测体积）；⑤密度 ρ=m/(V₂−V₁)。误差控制：先测质量再测体积（若"
     "先浸水，石块沾水使质量偏大、密度偏大）；要浸没且不碰壁不碰底。测不规则塑"
     "料块（密度比水小会漂浮）用「针压法」或「坠物法」（绑重物一起浸没再减去重"
     "物体积）。量筒读数：视线与凹液面最低处相平。",
     ["怎么测不规则物体的密度", "排水法测体积", "量筒读数注意事项",
      "测密度为什么要先测质量", "漂浮的物体怎么测密度", "针压法测密度"],
     ["问密度计算综合", "问实验顺序误差分析"],
     "atomic", "",
     "排水法：ρ=m/(V₂−V₁)；先测质量再测体积（防沾水误差大）；漂浮物用针压/坠物法；量筒读数视线与凹液面最低处相平。"),
    ("kp_card_cocomp",
     "CO 与 CO₂：组成相同性质迥异",
     "基础科学知识点内容（人话接口）", "化学",
     "一氧化碳（CO）和二氧化碳（CO₂）都由碳、氧两种元素组成，但每个 CO 分子比"
     " CO₂ 少一个氧原子——**分子构成不同，化学性质大不相同**：①CO 有毒（与血红"
     "蛋白结合）、CO₂ 无毒（但不供呼吸）；②CO 可燃（蓝色火焰），CO₂ 不燃不助燃"
     "（可灭火）；③CO 有还原性（炼铁），CO₂ 无还原性且有弱氧化性；④CO₂ 溶于水"
     "生成碳酸使石蕊变红，CO 不能。相互转化：CO 燃烧生成 CO₂（2CO+O₂→2CO₂）；"
     "CO₂ 与炽热碳高温生成 CO（CO₂+C→2CO）。这体现了「分子构成决定物质性质」—"
     "—结构决定性质的化学核心观念。",
     ["CO和CO₂的组成元素相同吗", "CO和CO₂性质为什么不同",
      "一氧化碳和二氧化碳怎么相互转化", "CO有什么用途", "分子构成决定性质举例"],
     ["问碳的氧化物价态变化", "问煤气中毒复习"],
     "atomic", "",
     "CO 与 CO₂ 同组成（碳氧两元素）异性质——分子构成不同（少一个氧原子）：CO 毒/可燃/还原性(炼铁)；CO₂ 无毒/不燃/灭火/碳酸；相互转化=燃与碳高温还原。"),
    ("kp_card_decomprole",
     "细菌和真菌在自然界中的作用",
     "基础科学知识点内容（人话接口）", "生物学",
     "多数细菌真菌作为**分解者**参与物质循环：把动植物遗体分解成二氧化碳、水和"
     "无机盐，归还大自然被植物重新吸收利用——没有它们，尸体粪便堆积如山、物质循"
     "环中断。此外：①引起动植物和人患病（寄生）——链球菌引起扁桃体炎、真菌引起"
     "足癣、棉花枯萎病；②与动植物共生——根瘤菌与豆科植物固氮、地衣（真菌+藻类"
     "）开垦岩石、肠道大肠杆菌合成维生素 K；③应用——制作发酵食品、生产抗生素、"
     "污水处理（活性污泥分解有机物）。抑制有害菌：低温保存（抑菌不杀菌）、巴斯德"
     "消毒、抗生素（灭细菌）、抗真菌药。细菌真菌是生态系统的「清道夫」兼「循环"
     "发动机」。",
     ["细菌和真菌在自然界中的作用", "分解者的作用是什么",
      "根瘤菌与豆科植物的共生关系", "地衣是什么", "污水处理利用什么原理",
      "为什么剩饭放久了会变酸"],
     ["问物质循环总复习", "问抗生素耐药机制"],
     "atomic", "",
     "细菌真菌=分解者：分解遗体成 CO₂ 水无机盐归还自然（物质循环发动机）；也寄生致病（链球菌/足癣）+共生（根瘤菌固氮/地衣/肠道菌）+应用（发酵/抗生素/污水处理）。"),
]

QUESTIONS = [
    ("QB-581", "怎么测不规则物体的密度", "物理学", "技术直答",
     ["排水法", "量筒"], "通识拓展111"),
    ("QB-582", "CO和CO₂性质为什么不同", "化学", "技术直答",
     ["分子构成"], "通识拓展111"),
    ("QB-583", "细菌和真菌在自然界中的作用", "生物学", "技术直答",
     ["分解者", "物质循环"], "通识拓展111"),
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
                               "level:L2", "status:verified", "batch:通识拓展111"],
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
    bank["version"] = "v2.3"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
