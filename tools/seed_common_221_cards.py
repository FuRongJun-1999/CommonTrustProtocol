# -*- coding: utf-8 -*-
"""seed_common_221_cards.py · 通识拓展批次221知识卡+题库（幂等·两卡精批次）

221：化学-料酒去腥的原理/生活常识-油温几成怎么判断
KCCS 四要素+题干原句触发词。三重预检：料酒（shelflife 卡保质期角度划界）
与油温判断双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_cookingwine",
     "料酒去腥的原理",
     "基础科学知识点内容（人话接口）", "化学",
     "料酒去腥的两重机制：①**溶解挥发**——腥味物质（胺类等）**易溶于酒精**"
     "，酒精沸点低（78°C）挥发时**把腥味物质一起带走**（所以料酒要趁锅温高"
     "时沿锅边淋入，高温才能挥发带走腥味——冷水下料酒等于白加）；②**酯化"
     "增香**——酒精与食物中的脂肪酸在加热下发生**酯化反应**，生成有香味的"
     "酯类。**误区**：「出锅前放料酒提香」——低温时酒精不挥发反而留酒味，"
     "应在**锅温最高时**放；③**替代**——没有料酒可用黄酒/白酒（用量减半），"
     "**啤酒炖肉**也别有风味（啤酒鸭）；④料酒含盐（调味用）不适合直接喝，"
     "「料酒不是啤酒」别当饮品。同族：姜葱去腥是吸附与掩盖，机制不同。",
     ["料酒去腥的原理", "料酒什么时候放", "料酒可以用什么代替",
      "啤酒炖肉为什么香", "料酒和黄酒的区别"],
     ["问美拉德反应（煎牛排）", "问饮酒适量"],
     "atomic", "",
     "料酒去腥=酒精溶解腥味物[胺类]+低沸点挥发带走（趁锅温高沿锅边淋）+酯化增香；误区=出锅前放低温酒精不挥发反留酒味；替代=黄酒/白酒减半/啤酒炖肉；料酒含盐调味用非饮品。"),
    ("kp_card_oiltemp",
     "油温几成怎么判断",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「几成油温」的筷子判断法（木筷插入油中看气泡）：①**一两成（30-50°C）"
     "**——筷子基本无反应：适合酱料/调料；②**三四成（100-120°C）**——筷子"
     "周围**细密小泡缓缓上浮**：适合滑炒肉片（肉不粘锅不老）；③**五六成（"
     "150-180°C）**——气泡**密集快速上翻**：适合一般炒菜/初炸；④**七八成"
     "（200°C+）**——筷子**急速翻滚大泡+噼啪响**：适合复炸酥脆。**重要误"
     "区**：「油冒烟才下菜」=油温已超 200°C 以上——**油烟含有害物（丙烯醛）"
     "且油脂已过度氧化**，此时下菜又致癌又毁营养；正确=**热锅冷油**（锅先烧"
     "热再放油，油微热即下料），既防粘又不冒烟。",
     ["油温几成怎么判断", "油温筷子测试", "热锅冷油是什么",
      "油冒烟了还能炒菜吗", "五六成油温是多少度"],
     ["问美拉德反应（煎牛排）", "问油烟健康（通风）"],
     "atomic", "",
     "油温判断=筷子法：一两成无反应/三四成细泡滑炒/五六成密泡炒菜初炸/七八成急泡复炸；误区=油冒烟才下菜（超 200°C 产丙烯醛伤身毁营养）；正确=热锅冷油防粘不冒烟。"),
]

QUESTIONS = [
    ("QB-865", "料酒去腥的原理是什么？为什么说料酒要趁锅热的时候放？", "化学", "技术直答",
     ["酒精", "溶解", "挥发", "酯化", "锅边", "高温"], "通识拓展221"),
    ("QB-866", "怎么用筷子判断油温的几成热？为什么说「油冒烟才下菜」是误区？", "生活常识", "技术直答",
     ["三四成", "五六成", "七八成", "冒烟", "丙烯醛", "热锅冷油"], "通识拓展221"),
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
                               "level:L2", "status:verified", "batch:通识拓展221"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v4.92"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
