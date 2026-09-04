# -*- coding: utf-8 -*-
"""seed_common_28_cards.py · 通识拓展批次28知识卡+题库（幂等）

28：化学-自来水净化/地理学-撒哈拉沙漠/生物学-ABO血型/物理学-惯性
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_waterpurify",
     "自来水净化的步骤",
     "基础科学知识点内容（人话接口）", "化学",
     "自来水厂净化水的主要流程：①沉淀——加絮凝剂（明矾）使悬浮小颗粒凝聚成大"
     "颗粒沉降；②过滤——通过砂滤池截留不溶性杂质；③吸附——活性炭吸附色素与"
     "异味；④消毒——通入氯气（或二氧化氯/臭氧）杀灭病菌。自来水虽经净化仍不"
     "是纯水，还含可溶性钙镁化合物——硬度较高的水烧开后水垢（碳酸钙/氢氧化镁"
     "沉淀）就是钙镁析出的结果。净化程度最高的方法：蒸馏（实验室制纯水）；沉淀"
     "过滤吸附属物理方法，杀菌消毒是化学变化。",
     ["自来水是怎么净化的", "自来水厂净水的步骤", "活性炭净水吸附什么",
      "水垢是怎么来的", "蒸馏和过滤哪个净化程度高", "明矾净水原理"],
     ["问纯净水与矿泉水标准", "问污水处理流程"],
     "atomic", "",
     "净水四步=沉淀(明矾絮凝)→过滤(砂滤)→吸附(活性炭)→消毒(氯气·化学变化)；水垢=钙镁析出；蒸馏净化程度最高。"),
    ("kp_card_sahara",
     "世界最大的沙漠：撒哈拉",
     "人文通识知识点内容（人话接口）", "地理学",
     "撒哈拉沙漠（Sahara）是世界最大的热带沙漠：位于非洲北部，面积约 906 万平"
     "方公里（与中国国土相当），横跨埃及/利比亚/阿尔及利亚/摩洛哥等十余国。气"
     "候极端干旱：部分区域连续多年无降雨，白天可超 50℃、夜间可近 0℃（沙漠昼夜"
     "温差大——沙石吸放热快）。若按「荒漠」广义定义（含极地冷荒漠），南极洲是"
     "世界最大荒漠——常考辨析点。撒哈拉并非全为沙丘：约四分之一是沙海，其余为"
     "砾漠/岩漠；地下有丰富的古地下水与石油资源。",
     ["世界最大的沙漠是哪个", "撒哈拉沙漠在哪个洲", "撒哈拉沙漠有多大",
      "沙漠昼夜温差为什么大", "南极洲是荒漠吗", "撒哈拉沙漠下雨吗"],
     ["问沙漠化治理", "问绿洲水文"],
     "atomic", "",
     "撒哈拉=非洲北部·约906万km²·最大热带沙漠(多国横跨)；昼夜温差大(沙石热容小)；广义最大荒漠=南极洲。"),
    ("kp_card_bloodtype",
     "ABO血型与输血原则",
     "基础科学知识点内容（人话接口）", "生物学",
     "ABO 血型系统按红细胞表面抗原分为 A、B、AB、O 四型：A 型有 A 抗原、B 型"
     "有 B 抗原、AB 型两者都有、O 型两者都无。输血以「同型输血」为原则——输错"
     "血型会引发凝集反应（免疫攻击）危及生命。O 型曾被称为「万能供血者」、AB 型"
     "「万能受血者」，但只是在缺乏同型血时的应急小量方案，现代输血学强调必须同"
     "型（还要做交叉配血试验）。Rh 血型是另一重要系统（中国汉族约 99% 为 Rh 阳"
     "性，「熊猫血」指 Rh 阴性）。血型由遗传决定、终生不变。",
     ["ABO血型有哪几种", "输血的原则是什么", "O型血是万能供血者吗",
      "熊猫血是什么血型", "血型会改变吗", "什么是交叉配血"],
     ["问稀有血型分布", "问骨髓移植血型转换"],
     "atomic", "",
     "ABO=A/B/AB/O(按红细胞抗原)；输血=同型原则+交叉配血；O「万能供」仅应急小量；熊猫血=Rh阴性(汉族约1%)。"),
    ("kp_card_inertia",
     "惯性：保持原有运动状态的性质",
     "基础科学知识点内容（人话接口）", "物理学",
     "惯性是物体保持原有运动状态不变的性质——牛顿第一定律：一切物体在不受外力"
     "时，总保持静止或匀速直线运动状态。生活中的惯性现象：汽车急刹车乘客向前倾"
     "（身体要保持原有前进速度）、跳远助跑（利用惯性跳得更远）、拍打衣服除尘（衣"
     "服动而灰尘因惯性留下）、泼水（盆停水因惯性飞出）。注意：惯性是物体的固有"
     "属性，一切物体任何时候都有惯性——只与质量有关（质量越大惯性越大），与速"
     "度无关；「受到惯性作用」的说法是错的（惯性不是力）。",
     ["什么是惯性", "急刹车时乘客为什么前倾", "惯性和质量有什么关系",
      "惯性是力吗", "跳远为什么要助跑", "什么是牛顿第一定律"],
     ["问二力平衡", "问摩擦力与运动分析"],
     "atomic", "",
     "惯性=保持原有运动状态的固有属性(牛顿第一定律)；只与质量有关与速度无关；不是力——「惯性作用」说法错误。"),
]

QUESTIONS = [
    ("QB-245", "自来水是怎么净化的", "化学", "技术直答",
     ["沉淀", "过滤", "消毒"], "通识拓展28"),
    ("QB-246", "世界最大的沙漠是哪个", "地理学", "技术直答",
     ["撒哈拉"], "通识拓展28"),
    ("QB-247", "ABO血型有哪几种", "生物学", "技术直答",
     ["A", "B", "AB", "O"], "通识拓展28"),
    ("QB-248", "急刹车时乘客为什么前倾", "物理学", "技术直答",
     ["惯性"], "通识拓展28"),
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
                               "level:L2", "status:verified", "batch:通识拓展28"],
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
    bank["version"] = "v1.20"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
