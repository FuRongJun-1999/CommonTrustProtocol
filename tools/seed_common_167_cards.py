# -*- coding: utf-8 -*-
"""seed_common_167_cards.py · 通识拓展批次167知识卡+题库（幂等·两卡精批次）

167：生物学-种子的传播方式/生活常识-水银温度计打碎了怎么办
KCCS 四要素+题干原句触发词。三重预检：种子传播（fruitform 卡讲果实形成未讲
传播）、水银泄漏（expansion 卡讲测温原理/汞卡讲化学性质，泄漏应急未覆盖）。
执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_seedspread",
     "种子的传播方式",
     "基础科学知识点内容（人话接口）", "生物学",
     "植物不能走路，种子「旅行」各有妙招：①**风力传播**——轻小带翅或带毛："
     "蒲公英「降落伞」（冠毛）、枫树/榆树「小翅膀」（翅果）、兰花粉尘般细微的"
     "种子；②**动物传播**——a.**搭便车**：苍耳/鬼针草的钩刺挂在动物皮毛上（"
     "尼龙搭扣的发明灵感）；b.**被吃带种**：樱桃/草莓的种子随动物吞食后排泄到"
     "远方（有些种子经消化道才易发芽）；③**水力传播**——椰子（能漂洋过海数"
     "月）、莲蓬随水漂流；④**自体弹射**——凤仙花（「急性子」）果荚一碰即炸"
     "裂弹射种子数米、喷瓜成熟后果实脱落时把种子连黏液喷出十几米。意义：传播"
     "=扩展领地、避免与「亲代」竞争阳光水分、减少同种拥挤——植物「卷」不过就"
     "「搬」的生存智慧。",
     ["种子靠什么传播", "蒲公英种子靠风传播", "苍耳挂在动物身上",
      "凤仙花弹射种子", "椰子靠什么传播", "种子传播方式有哪些"],
     ["问果实怎么形成的（用果实形成卡）", "问传粉与授粉"],
     "atomic", "",
     "种子传播四招=风力(蒲公英冠毛/枫翅果)+动物(苍耳钩挂搭车·果实被吃后排泄·樱桃经消化道助发芽)+水力(椰子漂洋/莲蓬漂流)+自体弹射(凤仙花/喷瓜)；意义=扩展领地避竞争——植物的生存智慧。"),
    ("kp_card_mercuryspill",
     "水银温度计打碎了怎么办",
     "生活常识知识点内容（人话接口）", "生活常识",
     "水银（汞）常温即缓慢**蒸发**，汞蒸气吸入有毒（损害神经系统/肾脏——儿童"
     "孕妇最敏感），体温计打碎的正确处理：①**开窗通风**（关掉房间其他门窗，"
     "加速汞蒸气排出，别站在下风向）；②**戴手套**用硬纸片/湿棉签**小心收集汞"
     "珠**（汞表面张力大成珠，可互相推拢合并），收入**密封瓶（加水覆盖防再蒸"
     "发）**交给社区危废或环保部门，勿随意丢弃；③散落缝隙的汞珠**洒硫磺粉**"
     "——硫与汞常温化合生成硫化汞（红棕色固体，不再挥发）；④**三个禁止**："
     "禁止用扫帚扫（打成更细小珠加速蒸发）、禁止用吸尘器（吸进去加热喷出更毒"
     "）、禁止用手直接接触。须知：一支体温计含汞约 0.5-1g，及时正确处理不必"
     "恐慌；水银体温计已全面禁产，电子体温计/红外额温枪更安全。",
     ["水银温度计打碎了怎么处理", "体温计水银有毒吗", "水银撒了能用扫帚吗",
      "硫磺粉除水银", "水银体温计还能用吗", "汞中毒怎么预防"],
     ["问误服汞的急救（立即就医）", "问电子体温计选购"],
     "atomic", "",
     "水银泄漏=开窗通风+戴手套硬纸片收集汞珠入密封水瓶（加水覆盖）+缝隙洒硫磺粉生成硫化汞；三禁=勿扫帚/勿吸尘器/勿手直接触（加速蒸发扩散）；汞蒸气伤神经肾脏儿童孕妇敏感；一支体温计正确处理不必恐慌——水银计已禁产改电子。"),
]

QUESTIONS = [
    ("QB-755", "蒲公英、苍耳、椰子的种子分别靠什么方式传播？种子传播对植物有什么意义？", "生物学", "技术直答",
     ["风力", "动物", "水力", "弹射", "苍耳", "椰子", "传播"], "通识拓展167"),
    ("QB-756", "水银温度计打碎了应该怎么处理？为什么不能用扫帚扫和吸尘器吸？", "生活常识", "技术直答",
     ["通风", "硫磺", "收集", "密封", "扫帚", "吸尘器", "蒸发"], "通识拓展167"),
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
                               "level:L2", "status:verified", "batch:通识拓展167"],
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
    bank["version"] = "v4.40"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
