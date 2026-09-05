# -*- coding: utf-8 -*-
"""seed_common_189_cards.py · 通识拓展批次189知识卡+题库（幂等·两卡精批次）

189：生活常识-蚊子包为什么痒/生物学-为什么会起鸡皮疙瘩
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（蜻蜓/雪吸音弱关联
弃选）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_mosquitobite",
     "蚊子包为什么痒",
     "生活常识知识点内容（人话接口）", "生活常识",
     "蚊子「咬」人的真相：①蚊子**不是咬**——用针状口器刺入皮肤并**注入唾液**"
     "（含**抗凝蛋白**防止血液凝固方便吸食）；②**痒和包是自己的免疫系统干的"
     "**——免疫系统识别到外来蛋白，释放**组胺**，组胺让毛细血管扩张渗出（红"
     "肿鼓包）+刺激神经末梢（痒）——反应越强包越大越痒（小孩初次被咬反应轻，"
     "反复叮咬后致敏反而更肿）；③**止痒**：肥皂水清洗（中和酸性刺激）、**冷"
     "敷**收缩血管止痒、炉甘石洗剂；**勿抓挠**——抓破继发感染（尤其糖尿病"
     "者）；④**驱蚊有效成分**：**避蚊胺（DEET）**、派卡瑞丁、柠檬桉油——「"
     "维生素 B1 驱蚊/超声波驱蚊器」均无证据。蚊子偏爱「呼出二氧化碳多、体温"
     "高、出汗多」的人。",
     ["蚊子包为什么痒", "被蚊子咬了怎么止痒", "蚊子唾液",
      "驱蚊什么成分有效", "维生素B1驱蚊是真的吗"],
     ["问过敏体质（就医）", "问登革热防护"],
     "atomic", "",
     "蚊子包痒=注入抗凝唾液→免疫释放组胺→血管渗出+痒（反应因人而异）；止痒=肥皂水+冷敷+炉甘石，勿抓挠防感染；驱蚊有效=避蚊胺 DEET/派卡瑞丁/柠檬桉油——B1/超声波驱蚊无证据；爱招蚊=CO₂ 多体温高出汗多。"),
    ("kp_card_goosebumps",
     "为什么会起鸡皮疙瘩",
     "基础科学知识点内容（人话接口）", "生物学",
     "起鸡皮疙瘩=**立毛肌收缩**：每根体毛根部都连着一小束平滑肌（立毛肌），受"
     "冷或应激时收缩，把毛发**竖立**起来，皮肤表面随之鼓起小凸点。**进化来"
     "源**：①**保暖**——毛发丰富的祖先竖毛后毛间空气层加厚锁温（人类毛发退"
     "化，只留下「鼓包」这个动作残留——保暖效果已无）；②**应激威吓**——猫狗"
     "受威胁时「炸毛」让自己看起来更大（同源机制）；③人类独有触发：听到**极"
     "度动人的音乐**时的「战栗」（frisson）也伴随鸡皮疙瘩——与多巴胺奖赏系"
     "统相关（能被音乐引发战栗的人约占 55-85%）。鸡皮疙瘩本身无害，几分钟自"
     "退；持续不退伴毛发角化（「鸡皮肤」）是另一回事（毛周角化症，良性）。",
     ["为什么会起鸡皮疙瘩", "立毛肌", "鸡皮疙瘩的作用",
      "听音乐起鸡皮疙瘩", "毛周角化"],
     ["问体温调节", "问毛周角化护理"],
     "atomic", "",
     "鸡皮疙瘩=立毛肌收缩竖毛：进化残留（祖先竖毛锁温保暖+应激炸毛威吓——猫炸毛同源）；人类毛发退化只留动作；音乐引发的战栗也与多巴胺奖赏相关；本身无害几分钟自退，持续的「鸡皮肤」=毛周角化症良性。"),
]

QUESTIONS = [
    ("QB-806", "被蚊子叮咬后为什么会起包发痒？哪些驱蚊成分被证明有效？", "生活常识", "技术直答",
     ["唾液", "组胺", "免疫", "避蚊胺", "DEET", "派卡瑞丁"], "通识拓展189"),
    ("QB-807", "人会起鸡皮疙瘩是什么机制？这个反应的进化来源是什么？", "生物学", "技术直答",
     ["立毛肌", "竖毛", "保暖", "应激", "进化残留"], "通识拓展189"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"frisson"}  # 正当术语（音乐战栗·法语借词）
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            if word not in whitelist:
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
                               "level:L2", "status:verified", "batch:通识拓展189"],
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
    bank["version"] = "v4.62"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
