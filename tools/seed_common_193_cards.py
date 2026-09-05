# -*- coding: utf-8 -*-
"""seed_common_193_cards.py · 通识拓展批次193知识卡+题库（幂等·两卡精批次）

193：生活常识-白头发的真相/生活常识-鱼刺卡喉的正确处理
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
    ("kp_card_whitehair",
     "白头发的真相",
     "生活常识知识点内容（人话接口）", "生活常识",
     "头发为什么变白：每根头发的颜色来自毛囊**黑色素细胞**生产的黑色素——"
     "随年龄增长黑色素细胞**逐渐停止工作**（遗传决定时间表），新长出的头发没"
     "有色素就是白的。**几个真相**：①「一夜白头」极少真的发生——多为「**斑"
     "秃**」：免疫攻击让黑发批量脱落（白发不受影响留存），黑白对比显得「全"
     "白」；②「拔一根长十根」是谣言——一个毛囊只长一根，拔了那根就没了，还"
     "可能伤毛囊发炎；③**少白头**=遗传主导，B12/铜/铁缺乏、甲状腺问题、重度"
     "压力有贡献（压力影响黑色素干细胞的研究存在但「逆转白发」无可靠方法）；"
     "④市面上「黑发丸/转黑洗发水」无科学证实的转黑能力——宣称能转黑的多是"
     "染发剂或心理安慰。",
     ["白头发是怎么来的", "一夜白头是真的吗", "拔白头发会长更多吗",
      "少白头怎么办", "白头发能变黑吗"],
     ["问染发频率与健康", "问脱发治疗（就医）"],
     "atomic", "",
     "白发=毛囊黑色素细胞停工（遗传定时间表）；一夜白头多为斑秃黑白对比错觉；拔一根长十根是谣言（一毛囊一根且伤毛囊）；少白头遗传主导+B12 铜铁缺乏/甲状腺有贡献；无科学证实的转黑方法。"),
    ("kp_card_fishbone",
     "鱼刺卡喉的正确处理",
     "生活常识知识点内容（人话接口）", "生活常识",
     "鱼刺卡喉**两大流传最广的错误**：①**吞饭团/馒头**——可能把刺**推得更"
     "深**（刺穿食管壁→纵隔感染，可致命）；②**喝醋**——醋软化鱼刺需要浸泡"
     "**数小时**，流过喉咙的几秒钟毫无作用，大量喝反而刺激黏膜。**正确做"
     "法**：①**停止吞咽**，轻咳——浅刺可能随气流出来；②张嘴用**手电照**，"
     "看得见的浅刺可用干净镊子取出；③看不见/咳不出/**卡得深（胸骨后疼"
     "痛）→立即就医**（耳鼻喉科喉镜/胃镜取出，几小时的事拖成大手术就亏"
     "了）；④儿童老人表达不清，直接就医。**预防**：吃鱼不说话笑闹、给小孩"
     "挑刺、细嚼慢咽。同系列：海姆立克（气道梗阻）、鱼刺（食管异物）是两个不"
     "同部位的急救。",
     ["鱼刺卡喉咙怎么办", "鱼刺卡喉喝醋有用吗", "吞饭团对不对",
      "鱼刺卡喉要就医吗", "鱼刺卡喉的正确处理"],
     ["问海姆立克（用海姆立克卡）", "问食管异物并发症"],
     "atomic", "",
     "鱼刺卡喉=停止吞咽→轻咳→可见浅刺镊取→深处立即就医耳鼻喉科；吞饭团=可能推深刺穿食管壁致命、喝醋=软化需数小时无作用还刺激黏膜——两大错误；预防=吃鱼不笑闹细嚼慢咽。"),
]

QUESTIONS = [
    ("QB-814", "白头发是怎么产生的？「一夜白头」和「拔一根长十根」的说法对吗？", "生活常识", "技术直答",
     ["黑色素", "毛囊", "斑秃", "谣言", "遗传"], "通识拓展193"),
    ("QB-815", "鱼刺卡喉咙时吞饭团、喝醋对不对？正确的处理方法是什么？", "生活常识", "技术直答",
     ["不对", "推深", "喝醋", "无效", "轻咳", "就医"], "通识拓展193"),
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
                               "level:L2", "status:verified", "batch:通识拓展193"],
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
    bank["version"] = "v4.66"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
