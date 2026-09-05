# -*- coding: utf-8 -*-
"""seed_common_213_cards.py · 通识拓展批次213知识卡+题库（幂等·两卡精批次）

213：生物学-「饿过劲」的血糖机制/生活常识-巴氏奶与常温奶
KCCS 四要素+题干原句触发词。三重预检：两主题双库零覆盖（血糖调节老卡为
稳态生理角度，饿过劲机制与巴氏奶常温奶划界）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_hungryover",
     "为什么饿过头反而不饿了",
     "基础科学知识点内容（人话接口）", "生物学",
     "「饿过劲」=血糖调节的典型表现：①饿的信号——血糖降低→下丘脑发出饥饿感"
     "（胃排空收缩+ghrelin 饥饿素升高）；②**持续不进食**→身体启动**后备供能"
     "**：肝糖原分解+**脂肪分解供能**+糖异生（蛋白质转糖），血糖回升——饥饿"
     "感暂时消失（「饿过劲」）；③**危险**：这个过程消耗肌肉、代谢废物堆积，"
     "长期饥一顿饱一顿打乱节律→胃病/胆结石/暴食倾向。**正确做法**：规律三餐"
     "；临时无法吃饭可先吃点坚果/香蕉垫底，避免血糖过山车。规律进食让血糖平"
     "稳，注意力与情绪也更稳定。",
     ["为什么饿过头就不饿了", "饿过劲是怎么回事", "血糖低了身体怎么办",
      "糖异生是什么", "饥一顿饱一顿的危害"],
     ["问糖尿病饮食（就医）", "问减肥饮食（用减重卡）"],
     "atomic", "",
     "饿过劲=血糖降低触发饥饿→持续不进食启动后备供能（肝糖原分解+脂肪供能+糖异生）血糖回升饥饿感暂消——消耗肌肉代谢废物堆积；规律三餐避免血糖过山车；临时垫底选坚果香蕉。"),
    ("kp_card_milktype",
     "巴氏奶与常温奶",
     "生活常识知识点内容（人话接口）", "生活常识",
     "牛奶两大类（按杀菌方式）：①**巴氏奶（鲜奶）**——**72-85°C** 低温巴氏"
     "杀菌几十秒：保留大部分活性蛋白与风味，**必须冷藏（4°C）**、保质期仅 "
     "5-7 天；②**常温奶（纯牛奶）**——**137°C 左右超高温瞬时灭菌（UHT）**+"
     "无菌包装：可常温存放 **6 个月**，但高温使部分水溶性维生素与活性蛋白损"
     "失、风味略带「蒸煮味」。**营养对比**：核心营养（蛋白质/钙）两者基本一"
     "致——钙不会因高温丢失；差异主要在少量维生素与活性物质。**选购**：按储"
     "存条件与饮用量选（喝得快选巴氏奶、囤货选常温奶）；「常温奶没营养」是误"
     "解——蛋白质和钙都在。",
     ["巴氏奶和常温奶的区别", "鲜奶和纯牛奶哪个好", "牛奶怎么杀菌的",
      "常温奶有营养吗", "牛奶保质期为什么不同", "UHT是什么"],
     ["问补钙（用骨骼卡）", "问酸奶发酵（用发酵卡）"],
     "atomic", "",
     "巴氏奶=72-85°C 低温杀菌：活性蛋白风味保留好但 4°C 冷藏仅 5-7 天；常温奶=137°C UHT 无菌包装常温 6 个月：蛋白质钙基本一致、少量维生素损失带蒸煮味；按饮用速度选——「常温奶没营养」是误解。"),
]

QUESTIONS = [
    ("QB-849", "为什么饿过头之后反而不饿了？长期饥一顿饱一顿有什么危害？", "生物学", "技术直答",
     ["肝糖原", "脂肪分解", "糖异生", "血糖回升", "节律"], "通识拓展213"),
    ("QB-850", "巴氏奶和常温奶的杀菌方式有什么不同？「常温奶没营养」的说法对吗？", "生活常识", "技术直答",
     ["巴氏杀菌", "72", "UHT", "超高温", "冷藏", "6个月"], "通识拓展213"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"ghrelin"}  # 正当术语（饥饿素）
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
                               "level:L2", "status:verified", "batch:通识拓展213"],
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
    bank["version"] = "v4.84"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
