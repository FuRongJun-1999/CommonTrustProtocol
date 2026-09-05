# -*- coding: utf-8 -*-
"""seed_common_214_cards.py · 通识拓展批次214知识卡+题库（幂等·两卡精批次）

214：生物学-饭后困倦的原理/食品工程-方便面为什么卷曲
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（饭后困与春困卡
[季节性]划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_postmeal",
     "饭后为什么会困",
     "基础科学知识点内容（人话接口）", "生物学",
     "饭后困倦的机制：①**血液重新分配**——进食后消化系统需要更多血流，大脑"
     "供血占比相对下降；②**食欲素下降**——进食后血糖升高促进胰岛素分泌，带"
     "动**色氨酸**更容易进入大脑转化为**5-羟色胺→褪黑素**（促睡链条）；③"
     "**高 GI 饮食加重困倦**——精制碳水（白米饭/面条/甜食）血糖大起大落，餐"
     "后困倦更明显。**缓解**：吃七分饱+蛋白质蔬菜搭配（降 GI）、餐后散步 10-"
     "15 分钟、午睡 20 分钟（超过 30 分钟进入深睡眠反而昏沉）。**注意**：每顿"
     "饭后都困到睁不开眼+多饮多尿，需排查血糖问题。",
     ["饭后为什么会困", "吃了饭就困怎么办", "餐后困倦的原因",
      "高GI食物", "饭后小睡多久合适"],
     ["问春困（用春困卡）", "问血糖健康"],
     "atomic", "",
     "饭后困=血液重分配向消化系统+血糖升高促胰岛素→色氨酸入脑转 5-羟色胺→褪黑素促睡链条；高 GI 精制碳水加重；缓解=七分饱+蛋白蔬菜搭配降 GI+餐后散步+午睡 20 分钟；每顿困到睁不开眼查血糖。"),
    ("kp_card_noodlecurl",
     "方便面为什么是卷曲的",
     "基础科学知识点内容（人话接口）", "生活常识",
     "方便面「卷发」的工程设计：①**增大受热面积**——卷曲面与油炸油接触面更"
     "大，**几十秒内均匀快速脱水**（直条面效率低易炸不透）；②**防粘连**——"
     "卷曲条互相支撑留有空隙，不会粘成一块「面饼疙瘩」；③**提高韧性**——卷"
     "曲结构缓冲运输挤压不易碎成渣；④**加快复水**——卷曲面表面积大，热水泡 "
     "3 分钟即可吸水回软（复水性好是方便面「方便」的核心）。面饼的「波浪」是"
     "切条后**传送带速度差+油炸定型**自然形成的。同思路：挂面是直的（晾晒工"
     "艺不同、煮的时间更长）。",
     ["方便面为什么是卷的", "方便面制作工艺", "面饼为什么卷曲",
      "方便面油炸", "方便面为什么泡三分钟"],
     ["问挂面（直条工艺）", "问方便面营养"],
     "atomic", "",
     "方便面卷曲=工程设计：卷曲增大油炸受热面积快速均匀脱水+防粘连+缓冲运输挤压+复水快（3 分钟泡开=方便核心）；波浪是传送带速度差+油炸定型自然形成；挂面直条是晾晒工艺不同。"),
]

QUESTIONS = [
    ("QB-851", "饭后为什么会犯困？怎么吃可以减轻餐后困倦？", "生物学", "技术直答",
     ["血液", "消化", "胰岛素", "色氨酸", "高GI", "散步"], "通识拓展214"),
    ("QB-852", "方便面为什么做成卷曲形状？卷曲的面条有什么好处？", "生活常识", "技术直答",
     ["受热面积", "油炸", "防粘连", "复水", "运输"], "通识拓展214"),
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
                               "level:L2", "status:verified", "batch:通识拓展214"],
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
    bank["version"] = "v4.85"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
