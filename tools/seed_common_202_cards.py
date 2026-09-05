# -*- coding: utf-8 -*-
"""seed_common_202_cards.py · 通识拓展批次202知识卡+题库（幂等·两卡精批次）

202：居家除害-蟑螂防治/生活常识-脚臭的防治
KCCS 四要素+题干原句触发词。三重预检：蟑螂双库零覆盖；脚臭双库零覆盖
（蚂蚁老卡为行为学角度弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_roach",
     "蟑螂的防治",
     "生活常识知识点内容（人话接口）", "生活常识",
     "蟑螂喜**温暖、潮湿、缝隙、黑暗**，夜行取食——防治核心=**断其生存条件**"
     "：①**断食水**——食物密封、垃圾不过夜、擦干水渍（蟑螂没水活不过一周，"
     "没食物却能活很久——**水源是命门**）；②**封缝隙**——瓷砖缝/管道孔/门"
     "窗缝用玻璃胶封堵（蟑螂扁如纸，3mm 缝隙即可藏身）；③**灭杀**——**胶饵"
     "**（点在缝隙角落，蟑螂取食回巢死亡，尸体粪便再传染同类=**连锁灭杀**，"
     "优于喷剂）；蟑螂屋（粘捕监测用）；④**卵鞘难杀**——蟑螂卵鞘对药物抗性"
     "强，需持续 2-4 周反复处理；勿直接踩爆卵鞘（会扩散）。发现一只通常意味"
     "着一窝——看到白天出没说明「虫满为患」更要彻底处理。",
     ["蟑螂怎么消灭", "家里有蟑螂怎么办", "蟑螂胶饵怎么用", "蟑螂卵",
      "蟑螂为什么打不死", "蟑螂白天出来"],
     ["问蚊子驱避（用蚊子卡）", "问灭蟑公司选择"],
     "atomic", "",
     "蟑螂防治=断食水（水源是命门没水活不过一周）+玻璃胶封缝隙(3mm 即可藏身)+胶饵连锁灭杀（回巢死传染同类优于喷剂）+持续 2-4 周处理卵鞘；勿踩爆卵鞘扩散；白天出没=虫满为患彻底处理。"),
    ("kp_card_footodor",
     "脚臭的防治",
     "生活常识知识点内容（人话接口）", "生活常识",
     "脚臭的真相=**汗液本身没味**，是皮肤表面细菌分解汗液与角质产生的**异味"
     "物质**（异戊酸等）——脚部汗腺密集（每只脚约 25 万个汗腺）+鞋袜包裹闷"
     "湿=细菌繁殖温床。**防治**：①每日洗脚**彻底擦干趾缝**（潮湿=细菌温床）；"
     "②**棉袜天天换**、鞋子**两双轮换晾 48 小时**（鞋内干燥需要时间）；③抗"
     "菌喷雾/足粉喷鞋内；④穿透气鞋，避免连续穿不透气胶鞋；⑤**真正的足癣（"
     "真菌感染）**=脱皮水疱瘙痒，需抗真菌药膏（与脚臭不同）；顽固脚臭排查真"
     "菌。误诊提醒：多汗症严重者可就医（外用氯化铝溶液有效）。",
     ["脚臭怎么根治", "脚臭是什么原因", "鞋臭怎么去除", "脚汗多怎么办",
      "脚臭和脚气的区别"],
     ["问足癣治疗（用脚气卡）", "问鞋垫选择"],
     "atomic", "",
     "脚臭=细菌分解汗液角质的异味物（汗本身无味）：每日洗脚擦干趾缝+棉袜天天换+两双鞋轮换晾 48h+抗菌喷雾足粉；足癣真菌是另一回事需抗真菌药；严重多汗就医氯化铝。"),
]

QUESTIONS = [
    ("QB-831", "家里有蟑螂怎么彻底消灭？为什么说胶饵比喷剂更有效？", "生活常识", "技术直答",
     ["断食水", "封缝隙", "胶饵", "连锁", "卵鞘", "水源"], "通识拓展202"),
    ("QB-832", "脚臭是怎么产生的？应该怎么预防和去除脚臭？", "生活常识", "技术直答",
     ["细菌", "分解", "汗液", "擦干趾缝", "轮换", "棉袜"], "通识拓展202"),
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
                               "level:L2", "status:verified", "batch:通识拓展202"],
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
    bank["version"] = "v4.75"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
