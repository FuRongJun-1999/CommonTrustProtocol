# -*- coding: utf-8 -*-
"""seed_common_222_cards.py · 通识拓展批次222知识卡+题库（幂等·两卡精批次）

222：生活常识-杨柳飞絮与过敏/生活技能-挑橙子的技巧
KCCS 四要素+题干原句触发词。三重预检：飞絮过敏（diffusion 卡仅扩散现象
举例划界）与挑橙子双库零覆盖。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_catkin",
     "杨柳飞絮与过敏",
     "生活常识知识点内容（人话接口）", "生活常识",
     "春天漫天「飞雪」=杨柳树的**种毛**（种子传播载体，雌株结果产生），**本"
     "身致敏率不高**——真正的春季过敏主凶是**风媒花粉**（柏树/梧桐/桦树等"
     "看不见的花粉）。但飞絮**携带花粉、灰尘与污染物**，刺激眼鼻呼吸道，加"
     "重过敏与不适（飞絮期与花粉期重叠）。**防护**：①外出戴**口罩+护目镜/密"
     "封眼镜**；②回家**冲洗鼻腔**（生理盐水）、清洗眼脸与衣物；③室内关纱"
     "窗、用空气净化器；④过敏症状明显（喷嚏连发/眼痒/皮疹）用抗组胺药或鼻"
     "喷激素（遵医嘱）。飞絮还易燃——**勿点燃飞絮**（火灾隐患）。城市治理："
     "注射抑花剂、更换雄株、洒水湿化。",
     ["杨柳絮过敏怎么办", "飞絮是什么", "飞絮期如何防护", "飞絮是花粉吗",
      "飞絮能点燃吗"],
     ["问花粉过敏（就医）", "问生理盐水洗鼻"],
     "atomic", "",
     "杨柳飞絮=雌株种毛（种子载体）本身致敏率低，但携带花粉灰尘刺激眼鼻加重过敏；防护=口罩护目镜+回家冲洗鼻腔+关纱窗空净；勿点燃飞絮（易燃火灾隐患）；城市治理=抑花剂/换雄株/洒水湿化。"),
    ("kp_card_pickorange",
     "挑橙子的技巧",
     "生活常识知识点内容（人话接口）", "生活常识",
     "挑橙子三看一掂：①**看肚脐**——**肚脐小或无脐**的甜（大脐/open脐的多"
     "为「公母」误区其实是次果，水分易流失）；②**看表皮**——**细腻光亮毛孔"
     "细密**的皮薄肉厚；毛孔粗大粗糙的多皮厚；③**掂重量**——同样大小选**沉"
     "的**（水分足）；④**按压**——硬实有弹性=新鲜多汁；软塌=失水或过熟。"
     "**额外**：橙子底部圆圈小而白的更甜（品种也有关系）；「橙子越光滑越好"
     "打蜡」——食用蜡合规无害，介意可温水洗。橙子富含维生素 C，常温阴凉放"
     "置（冷藏过久影响风味）。",
     ["怎么挑橙子", "橙子肚脐大的好还是小的好", "橙子沉的好还是轻的好",
      "橙子打蜡能吃吗", "挑橙子的方法"],
     ["问挑柚子（用柚子卡）", "问维生素 C"],
     "atomic", "",
     "挑橙子=肚脐小或无脐的甜+表皮细腻毛孔细密皮薄+同大小掂重水分足+按压硬实有弹性；食用蜡合规温水洗即可；维C 富集常温阴凉存放。"),
]

QUESTIONS = [
    ("QB-867", "春天的杨柳飞絮本身是过敏原吗？飞絮期应该如何防护？", "生活常识", "技术直答",
     ["种毛", "花粉", "携带", "口罩", "冲洗鼻腔", "易燃"], "通识拓展222"),
    ("QB-868", "怎么挑到皮薄肉甜的橙子？橙子表面的蜡能吃吗？", "生活常识", "技术直答",
     ["肚脐", "小", "表皮细腻", "掂重", "食用蜡", "温水洗"], "通识拓展222"),
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
                               "level:L2", "status:verified", "batch:通识拓展222"],
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
    bank["version"] = "v4.93"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
