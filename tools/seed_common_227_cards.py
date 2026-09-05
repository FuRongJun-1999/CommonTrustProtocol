# -*- coding: utf-8 -*-
"""seed_common_227_cards.py · 通识拓展批次227知识卡+题库（幂等·两卡精批次）

227：传统文化-冬至吃饺子/生活常识-年糕的寓意
KCCS 四要素+题干原句触发词。三重预检：冬至饺子习俗（earthrotation 卡仅公转
节气划界）与年糕双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_wintersolstice",
     "冬至为什么要吃饺子",
     "人文通识知识点内容（人话接口）", "生活常识",
     "冬至吃饺子的习俗源自**医圣张仲景**的传说：东汉末年张仲景告老还乡（河南"
     "南阳），见乡亲们冬天**耳朵被冻烂**，便搭棚施药，把驱寒药材（羊肉/辣椒/"
     "驱寒草药）用面皮包成**耳朵形状**的「**祛寒娇耳汤**」施舍给百姓——从冬"
     "至吃到除夕，冻耳治好了。后人模仿「娇耳」包成食物，形成冬至吃饺子的习"
     "俗，谚语「**冬至不端饺子碗，冻掉耳朵没人管**」。**冬至的意义**——北半"
     "球白昼最短的一天，「冬至大如年」；「数九」从冬至开始（一九二九不出手…"
     "…九九加一九耕牛遍地走）。注意：北方吃饺子、南方多地吃**汤圆**（「吃了"
     "汤圆大一岁」）——南北习俗有别。",
     ["冬至为什么要吃饺子", "张仲景饺子传说", "祛寒娇耳汤",
      "冬至不端饺子碗", "数九从哪天开始", "冬至南方吃什么"],
     ["问汤圆（用汤圆卡）", "问二十四节气（用节气卡）"],
     "atomic", "",
     "冬至吃饺子=纪念医圣张仲景「祛寒娇耳汤」施药治冻耳的传说[谚语：冬至不端饺子碗冻掉耳朵没人管]；冬至=北半球白昼最短「大如年」+数九从此开始；北方饺子南方汤圆[吃了汤圆大一岁]——南北有别。"),
    ("kp_card_niangao",
     "年糕的寓意",
     "生活常识知识点内容（人话接口）", "生活常识",
     "年糕=春节传统食品，谐音「**年年高**」（年高升——生活/事业步步高升的吉"
     "祥寓意）。①**原料与做法**——糯米或米粉蒸制（可加红枣/豆沙/桂花），北"
     "方多为甜口（蒸/炸），南方有宁波水磨年糕（切片炒/汤——青菜肉丝炒年糕"
     "是家常经典）；②**各地特色**——北京白年糕、江南水磨年糕、福建红糖年"
     "糕、广东萝卜糕（虾米腊味）；③**保存**——阴凉通风短存或切片冷冻（冷藏"
     "会变硬回生——淀粉回生同面包原理）。**提示**：糯米黏滞难消化，肠胃弱者"
     "浅尝即可；糖尿病者注意（糯米升糖快）。",
     ["年糕的寓意", "年糕为什么叫年糕", "年糕是哪里的特产",
      "宁波水磨年糕", "年糕怎么保存"],
     ["问汤圆（用汤圆卡）", "问糯米消化"],
     "atomic", "",
     "年糕谐音「年年高」=春节吉祥食品：糯米/米粉蒸制（北方甜口蒸炸/南方宁波水磨年糕炒汤/广东萝卜糕）；保存=阴凉短存或切片冷冻（冷藏回生变硬同面包原理）；糯米黏滞难消化肠胃弱浅尝、升糖快糖尿病人注意。"),
]

QUESTIONS = [
    ("QB-880", "冬至吃饺子的习俗与哪位历史人物有关？「祛寒娇耳汤」是什么？", "生活常识", "技术直答",
     ["张仲景", "冻耳", "娇耳", "驱寒", "耳朵"], "通识拓展227"),
    ("QB-881", "年糕的寓意是什么？宁波水磨年糕是哪里的特色？", "生活常识", "技术直答",
     ["年年高", "宁波", "糯米", "南方"], "通识拓展227"),
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
                               "level:L2", "status:verified", "batch:通识拓展227"],
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
    bank["version"] = "v4.98"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
