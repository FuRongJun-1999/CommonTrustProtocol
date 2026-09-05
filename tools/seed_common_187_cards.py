# -*- coding: utf-8 -*-
"""seed_common_187_cards.py · 通识拓展批次187知识卡+题库（幂等·两卡精批次）

187：自然观察-松果的开合与湿度/生物学-竹子为什么长得快
KCCS 四要素+题干原句触发词。三重预检：松果开合（fibonacci 卡仅数学螺旋角
度）、竹子生长（panda 卡仅食物提及）主题均未覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_pinecone",
     "松果为什么遇湿会闭合",
     "基础科学知识点内容（人话接口）", "生物学",
     "松果鳞片会随**空气湿度**自动开合——干燥时张开（鳞片 basi 层/纤维层吸湿"
     "程度不同产生**不均匀膨胀**，片层向外翘起释放种子）、潮湿时闭合（护住种"
     "子不被雨水泡坏/避免在不适合传播的雨天散播）。这是**纯物理的湿度响应**："
     "不需要能量、不需要生命活动——**干枯多年的松果依然会开合**（所以松果是"
     "天然的「湿度计」：挂一个松果在门口，闭合=要下雨，张开=天气晴好——民间"
     "天气谚语的来源）。仿生应用：建筑学家据此设计**随湿度自动开合的木质表皮"
     "（不用电的「呼吸幕墙」）**、湿度响应的包装材料。同类现象：麦芒/燕麦芒的"
     "运动、木质门窗「梅雨关不上」——都是木材纤维吸湿不均匀胀缩。",
     ["松果为什么遇水闭合", "松果能预报天气吗", "松果开合的原理",
      "仿生建筑", "松果湿度计"],
     ["问斐波那契螺旋（用斐波那契卡）", "问木材特性"],
     "atomic", "",
     "松果鳞片=双层纤维吸湿不均匀胀缩的纯物理开合：干燥张开撒种/潮湿闭合护种——干枯多年仍开合（天然湿度计：闭合=要下雨）；仿生=免电呼吸幕墙；同类=木门梅雨关不上。"),
    ("kp_card_bamboogrowth",
     "竹子为什么长得那么快",
     "基础科学知识点内容（人话接口）", "生物学",
     "毛竹旺季一天能长 **1 米**，是植物界的「生长冠军」：①**秘诀=节间分裂组"
     "织同时活跃**——一般植物只在茎**顶端**生长点分裂细胞，而竹子的**每一个"
     "节间都有分生组织同时伸长**——几十个节一起「拔」，速度自然惊人；②笋期"
     "就把所有节与叶芽都预构建好（「笋有多大竹就有多粗」——出土后只做拉长，"
     "不再加粗）；③竹子其实是**草本（禾本科）**不是树——竹秆是中空的结构力"
     "学设计（轻而抗弯，模仿它的建筑与自行车架）；④**竹子开花是噩耗**——多"
     "数竹种一生只开一次花，开花后整片竹林同步枯死（周期可达数十年，大熊猫栖"
     "息地曾因竹子开花发生食物危机）。竹子快生+固碳强+可降解——环保材料之星。",
     ["竹子为什么长得快", "竹子一天能长多高", "竹子是树还是草",
      "竹子开花为什么可怕", "竹子的结构"],
     ["问大熊猫（用大熊猫卡）", "问速生树种对比"],
     "atomic", "",
     "竹子长得快=每个节间都有分生组织同时伸长（一般植物只在顶端）——旺季日长 1 米；笋期预构建只拉长不加粗；竹=禾本科草本非树（中空结构力学）；开花即整片枯死周期数十年=噩耗；快生固碳强=环保之星。"),
]

QUESTIONS = [
    ("QB-802", "松果为什么会随空气湿度自动开合？为什么说松果是天然的「湿度计」？", "生物学", "技术直答",
     ["吸湿", "不均匀膨胀", "物理", "闭合", "下雨", "仿生"], "通识拓展187"),
    ("QB-803", "竹子为什么长得特别快？竹子是树还是草？", "生物学", "技术直答",
     ["节间", "分生组织", "同时", "1米", "草本", "禾本科"], "通识拓展187"),
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
                               "level:L2", "status:verified", "batch:通识拓展187"],
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
    bank["version"] = "v4.60"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
