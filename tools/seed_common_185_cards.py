# -*- coding: utf-8 -*-
"""seed_common_185_cards.py · 通识拓展批次185知识卡+题库（幂等·两卡精批次）

185：生活常识-秋冬皮肤干燥护理/生活常识-挑鱼的技巧
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_dryskin",
     "秋冬皮肤干燥脱屑怎么办",
     "生活常识知识点内容（人话接口）", "生活常识",
     "秋冬皮肤干燥脱屑的根源=**皮脂分泌减少+环境湿度下降**，皮肤屏障锁不住水"
     "分。**反而加重干燥的习惯**：①洗澡水**过热**（舒服但洗掉皮脂膜）；②洗"
     "澡**时间过长**（超过 15 分钟）；③**天天用力搓澡**（把本就不足的角质层"
     "搓掉）；④碱性强的肥皂。**正确护理**：①水温 37-40°C、10-15 分钟内洗"
     "完；②**沐浴后 3 分钟内**涂身体乳（黄金窗口——皮肤还有湿度时锁水效果最"
     "好），干痒部位选含**尿素/神经酰胺/凡士林**成分的；③室内加湿（40-60%"
     "湿度）；④贴身衣物选纯棉，化纤毛料直接接触易痒。**就医线**：瘙痒影响睡"
     "眠、出现红斑丘疹脱屑大片（湿疹/银屑病等）、老年人下肢片状网状裂纹（「"
     "乏脂性湿疹」也需药膏干预）——别硬扛。",
     ["秋冬皮肤干燥怎么办", "身体乳什么时候涂最好", "搓澡好不好",
      "皮肤痒是什么原因", "洗澡水温多少合适"],
     ["问湿疹治疗（就医）", "问加湿器选购"],
     "atomic", "",
     "秋冬皮肤干燥=皮脂减少+湿度下降屏障锁水差；加重习惯=过热水澡/久洗/天天搓澡/碱性肥皂；护理=37-40°C 十五分钟内洗+沐浴后 3 分钟内涂身体乳（尿素/神经酰胺/凡士林）+室内湿度 40-60%；影响睡眠或红斑大片就医。"),
    ("kp_card_pickfish",
     "挑鱼的技巧",
     "生活常识知识点内容（人话接口）", "生活常识",
     "挑新鲜鱼五看：①**看眼球**——新鲜鱼眼球**清亮饱满凸起**、角膜透明；眼"
     "球凹陷浑浊发白=不新鲜；②**看鱼鳃**——掀开鳃盖，鳃片**鲜红或暗红、黏"
     "液清亮**；发灰发绿发黑有黏腻臭味=变质；③**按鱼肉**——手指按压**有弹"
     "性、凹陷快速回弹**；按下去凹坑不回弹=不新鲜；④**闻气味**——淡淡海水"
     "咸味或泥土腥味正常；**氨水味/腐臭味**=蛋白质分解变质；⑤**看鳞片与肛"
     "门**——鳞片有光泽紧贴不易脱落、肛门清爽内收（发灰外翻=不新鲜）。**保"
     "存**：现杀现吃最好；冷藏 0-4°C 一天内，冷冻 -18°C 可存数月（解冻后勿"
     "再冷冻）。淡水鱼与活鱼：看游动状态活泼、体表无伤无充血。",
     ["怎么挑新鲜的鱼", "看鱼鳃判断新鲜", "鱼眼清亮", "鱼不新鲜的表现",
      "鱼怎么保存"],
     ["问海鲜过敏（就医）", "问鱼的做法"],
     "atomic", "",
     "挑鱼五看=眼球清亮凸起+鳃鲜红黏液清亮+按压弹回+无氨臭味+鳞片紧贴肛门内收；氨水味/凹坑不回弹=变质勿吃；冷藏一天内冷冻 -18°C 数月，解冻后勿再冻；活鱼看游动活泼体表无伤。"),
]

QUESTIONS = [
    ("QB-798", "秋冬皮肤干燥脱屑是什么原因？为什么说洗澡后 3 分钟内涂身体乳效果最好？", "生活常识", "技术直答",
     ["皮脂", "湿度", "屏障", "尿素", "神经酰胺", "凡士林"], "通识拓展185"),
    ("QB-799", "怎么判断一条鱼新不新鲜？不新鲜的鱼有哪些表现？", "生活常识", "技术直答",
     ["眼球", "清亮", "鱼鳃", "鲜红", "弹性", "氨水"], "通识拓展185"),
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
                               "level:L2", "status:verified", "batch:通识拓展185"],
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
    bank["version"] = "v4.58"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
