# -*- coding: utf-8 -*-
"""seed_common_373_cards.py · 通识拓展批次373知识卡+题库（幂等）

373：生活现象小问答——3 张新卡（打喷嚏/仙人掌/月饼）+ 1 张存量卡补题
    （噪声与控制噪声三环节 kp_card_noise3 已在库，补 QB-1355）。
KCCS 四要素+题干原句触发词。预检已过（QB-1355~1358 可用，
打喷嚏/仙人掌/月饼在题库 0 覆盖，noise3 卡无对应题）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_sneeze",
     "打喷嚏",
     "生活常识知识点内容（人话接口）", "健康与身体",
     "打喷嚏——鼻腔的「自动清扫」：①**为什么会打**——灰尘/花粉/病菌/"
     "冷空气或刺激性气味进入鼻腔，刺激鼻黏膜上的神经末梢，信号传到大脑，"
     "触发「喷嚏反射」：先深吸一口气，声门突然紧闭，胸腹部肌肉猛烈收缩，"
     "一股高速气流从鼻腔冲出（速度可达每秒几十米），把异物和刺激物喷出去；"
     "②**为什么憋不得**——憋住喷嚏，高压气流会转向中耳（通过咽鼓管）和"
     "鼻窦，可能震伤耳膜、引发鼻窦炎症；病菌也会被压进耳朵和鼻窦；③**"
     "卫生礼仪**——喷嚏飞沫携带大量病菌（感冒/流感传播的主要途径之一），"
     "要用纸巾或手肘内侧遮挡口鼻，不要对着人打；④**连续打喷嚏**——"
     "过敏性鼻炎的典型表现（晨起连打好几个+流清鼻涕），需防过敏原而非"
     "单纯「着凉」。",
     ["为什么会打喷嚏", "打喷嚏为什么不能憋", "憋喷嚏有什么危害",
      "连续打喷嚏是怎么回事", "喷嚏的速度有多快", "打喷嚏礼仪"],
     ["问鼻窦炎治疗", "问感冒用药"],
     "atomic", "",
     "打喷嚏=灰尘花粉病菌冷空气刺激鼻黏膜神经触发喷嚏反射+深吸气声门紧"
     "闭胸腹猛收缩高速气流冲出鼻腔把异物喷出去+憋喷嚏高压气流转向咽鼓管"
     "鼻窦可能震伤耳膜引发炎症+飞沫带病菌用纸巾或手肘遮挡+晨起连续打喷嚏"
     "流清涕是过敏性鼻炎典型表现防过敏原。"),
    ("kp_card_cactus",
     "仙人掌",
     "植物常识知识点内容（人话接口）", "自然与生物",
     "仙人掌——沙漠里的「储水罐」：①**刺是叶子**——仙人掌的刺是退化"
     "的叶（变态叶）：沙漠干旱，宽大的叶子会让水分大量蒸发，叶退化成刺"
     "把蒸腾面积降到最小，同时防止动物啃食；光合作用的任务交给绿色肥厚"
     "的肉质茎；②**怎么储水**——肉质茎表皮有蜡质层锁水，内部组织能储存"
     "大量水分；根系浅而铺得开，一场小雨就能快速吸收地表水；③**为什么"
     "耐旱**——气孔夜间才打开（夜间温度低蒸发少，白天闭合锁水），这种"
     "「晚上开窗换气」的代谢方式是旱生植物的生存绝招；④**家养提示**——"
     "仙人掌烂根多是浇水太勤，宁干勿湿；⑤**辨析**——不是所有植物刺都是"
     "叶（月季的刺是茎表皮突起，与仙人掌的刺来源不同）。",
     ["仙人掌为什么耐旱", "仙人掌的刺是叶子吗", "仙人掌怎么储水",
      "仙人掌多久浇一次水", "变态叶是什么", "沙漠植物怎么生存"],
     ["问多肉植物", "问热带雨林植物"],
     "atomic", "",
     "仙人掌=刺是退化的变态叶减少蒸腾面积防啃食光合作用交给绿色肉质茎+"
     "茎蜡质层锁水内部储水根系浅而广雨后快速吸水+气孔夜间开放白天闭合"
     "锁水的旱生代谢+家养宁干勿湿浇水太勤烂根+月季刺是茎表皮突起与叶"
     "来源不同。"),
    ("kp_card_mooncake",
     "月饼",
     "传统美食知识点内容（人话接口）", "传统文化",
     "月饼——中秋的「团圆符号」：①**为什么中秋吃**——月饼形圆似满月，"
     "象征团圆；中秋祭月习俗由来已久，宋代文献已有「月饼」之名，明代起"
     "中秋吃月饼成为全国性习俗；民间还流传月饼传起义消息的传说故事；②**"
     "经典门派**——广式（皮薄馅足，莲蓉蛋黄）、苏式（层层起酥，鲜肉）、"
     "京式（自来红/自来白）、滇式（云腿月饼）各具风味；③**怎么保存**——"
     "传统月饼糖多油大水分少，常温阴凉干燥处可放较久；新式低糖/鲜肉月饼"
     "水分高易变质，需冷藏并尽快吃完；冷藏会让饼皮变硬，吃前回温口感好；"
     "④**健康提醒**——月饼高油高糖，一次别吃太多，老人小孩浅尝即可。",
     ["中秋节为什么吃月饼", "月饼怎么保存", "月饼有哪些流派",
      "广式苏式月饼区别", "月饼能放冰箱吗", "月饼的由来"],
     ["问端午粽子", "问元宵汤圆"],
     "atomic", "",
     "月饼=形圆似满月象征团圆宋代有月饼之名明代成中秋习俗+广式莲蓉蛋黄"
     "苏式起酥鲜肉京式自来红滇式云腿四大门派+传统糖多油大常温阴凉可放"
     "低糖鲜肉月饼易变质需冷藏尽快吃完冷藏饼皮变硬回温再吃+高油高糖适"
     "量浅尝。"),
]

QUESTIONS = [
    ("QB-1355", "噪音为什么会影响健康？多少分贝算噪音？怎么隔音？",
     "生活常识", "技术直答",
     ["噪音", "分贝", "听力", "隔音"], "通识拓展373·存量卡补题"),
    ("QB-1356", "为什么会打喷嚏？为什么不能憋着不打？",
     "健康与身体", "技术直答",
     ["喷嚏", "鼻腔", "憋", "飞沫"], "通识拓展373"),
    ("QB-1357", "仙人掌为什么耐旱？它的刺是叶子吗？",
     "自然与生物", "技术直答",
     ["仙人掌", "耐旱", "刺", "沙漠"], "通识拓展373"),
    ("QB-1358", "中秋节为什么要吃月饼？月饼怎么保存比较好？",
     "传统文化", "技术直答",
     ["月饼", "中秋", "团圆", "保存"], "通识拓展373"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展373"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.43"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
