# -*- coding: utf-8 -*-
"""seed_common_201_cards.py · 通识拓展批次201知识卡+题库（幂等·两卡精批次）

201：生活常识-挑螃蟹与死蟹安全/生活常识-家庭急救箱配置
KCCS 四要素+题干原句触发词。三重预检：挑活蟹/死蟹安全主题未覆盖（foodmyth
卡是相克辟谣角度）；家庭急救箱零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_pickcrab",
     "挑螃蟹与死蟹安全",
     "生活常识知识点内容（人话接口）", "生活常识",
     "挑活蟹三看：①**看活性**——翻过来能迅速翻身、触碰眼睛会缩、吐泡多（吐"
     "泡=呼吸活跃）；②**捏蟹腿**——蟹腿**硬实有劲**（捏不下陷）的肉满（软"
     "腿=瘦蟹或刚脱壳）；③**掂重与看腹部**——同大小掂重的肥；腹部（脐）发"
     "亮的膏黄足。**死蟹安全要点（重要）**：**河蟹/大闸蟹必须活煮**——蟹体"
     "内组氨酸死后快速分解为**组胺**（过敏毒素，加热不破坏），死越久毒越多，"
     "吃了可能过敏中毒；**海蟹可冰鲜短期保存**（死亡后尽快冷冻）。蒸制：水开"
     "后 15-20 分钟（视大小）+**姜醋驱寒去腥**。孕妇/痛风患者慎食（嘌呤高）。",
     ["怎么挑螃蟹", "死螃蟹能吃吗", "大闸蟹为什么必须活煮",
      "螃蟹组胺中毒", "蒸螃蟹要多久", "螃蟹和柿子能一起吃吗"],
     ["问食物相克辟谣（用相克卡）", "问海鲜过敏（就医）"],
     "atomic", "",
     "挑活蟹=翻身快+蟹腿硬实有劲+掂重腹亮；河蟹必须活煮——死后组氨酸快速分解组胺（加热不破坏）过敏中毒，海蟹死可尽快冷冻；蒸 15-20 分钟姜醋；痛风孕妇慎食——「螃蟹+柿子中毒」实为变质或鞣酸问题非相克。"),
    ("kp_card_firstaidkit",
     "家庭急救箱配置",
     "生活常识知识点内容（人话接口）", "生活常识",
     "家庭急救箱基础清单：①**器械**：电子/水银体温计、血压计（家有老人）、**"
     "镊子、小剪刀、一次性手套**；②**消毒耗材**：碘伏棉签（比酒精温和不刺"
     "痛）、无菌纱布、创可贴（多规格）、医用胶带、弹力绷带；③**常用药**：退"
     "烧药（对乙酰氨基酚/布洛芬——按家庭成员配置）、口服补液盐、抗过敏药（"
     "氯雷他定）、腹泻用药；④**应急物品**：冰袋（常备冰箱）、烫伤膏、生理盐"
     "水冲洗液；⑤**信息卡**：紧急联系电话/血型/过敏史。**管理**：阴凉干燥儿"
     "童够不到处存放；**每半年检查一次效期**（过期药及时更换——过期药交药店"
     "回收点勿随意丢弃）；家中有慢性病者加配常用药与说明卡。",
     ["家庭急救箱要配什么", "急救箱放哪里", "过期药品怎么处理",
      "家庭常备药清单", "碘伏和酒精的区别"],
     ["问外伤处理（用RICE/烫伤卡）", "问老人家庭监测"],
     "atomic", "",
     "家庭急救箱=器械(体温计血压计镊剪手套)+消毒(碘伏棉签纱布创可贴绷带)+常用药(退烧补液盐抗过敏)+应急(冰袋烫伤膏生理盐水)+信息卡(电话血型过敏史)；阴凉儿童难及处存放、每半年查效期、过期药交回收点。"),
]

QUESTIONS = [
    ("QB-829", "怎么挑到肉肥的活螃蟹？为什么死的大闸蟹不能吃？", "生活常识", "技术直答",
     ["活性", "翻身", "蟹腿", "组胺", "活煮", "河蟹"], "通识拓展201"),
    ("QB-830", "家庭急救箱应该配置哪些物品？过期药品应该怎么处理？", "生活常识", "技术直答",
     ["体温计", "碘伏", "纱布", "补液盐", "效期", "回收"], "通识拓展201"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展201"],
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
    bank["version"] = "v4.74"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
