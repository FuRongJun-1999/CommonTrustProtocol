# -*- coding: utf-8 -*-
"""seed_common_206_cards.py · 通识拓展批次206知识卡+题库（幂等·两卡+触发词补强）

206：生活常识-护肤的正确顺序/生活常识-熬夜后的补救
+ 触发词补强：athletesfoot/acnecare 卡生效条件补口语短触发词（短触发复测二
暴露的缺口）。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_skincareroutine",
     "护肤品的正确使用顺序",
     "生活常识知识点内容（人话接口）", "生活常识",
     "护肤顺序口诀=**「先水后乳、先轻薄后厚重」**（分子小/质稀的先用，让后续"
     "更好吸收）：①**洁面**（早晚温和洁面）；②**化妆水/爽肤水**——二次清洁"
     "+补水打底；③**精华**（功效成分浓度最高，抗老/美白/修护按需）；④**乳"
     "液/面霜**（锁水封闭——乳液夏天、面霜干季）；⑤**白天最后一步=防晒**（"
     "最重要也最常被省略——紫外线是皮肤老化主因，阴天也有紫外线）；⑥夜间可"
     "用视黄醇/A 醇类（**只晚上用**，见光分解且刺激，需建立耐受+严格防晒）。"
     "**误区**：叠加越多越好=错（太多层反而搓泥闷痘）；眼霜非必需（面霜可"
     "代）——按皮肤状态做减法。",
     ["护肤品使用顺序", "化妆水精华乳液先用哪个", "防晒是最后一步吗",
      "视黄醇怎么用", "护肤步骤", "眼霜有必要吗"],
     ["问防晒霜（用防晒卡）", "问痤疮护理（用痤疮卡）"],
     "atomic", "",
     "护肤顺序=洁面→化妆水打底→精华→乳液/面霜锁水→白天最后防晒（紫外线=老化主因阴天也有）；视黄醇 A 醇只晚上用需建立耐受；叠加并非越多越好按状态做减法。"),
    ("kp_card_stayuprecover",
     "熬夜后的补救",
     "生活常识知识点内容（人话接口）", "生活常识",
     "不得不熬夜后的科学补救：①**次日补觉讲策略**——当晚睡到自然醒+**午后小"
     "睡 20-30 分钟**（别睡一下午——打乱节律更疲惫）；②**水分+蛋白质**——熬"
     "夜失水多，多喝水；早餐高蛋白（蛋/奶）+适量碳水，少油炸；③**光照管理**"
     "——白天多晒太阳重置生物钟、**晚上继续按正常时间睡**（别提前 8 点睡）；"
     "④**咖啡因有时限**——下午 2 点后别喝（半衰期 5-6 小时，影响当晚入睡）；"
     "⑤**认清底线**：熬夜的伤害（记忆/免疫/代谢）只能减少不能抵消——「熬最"
     "深的夜用最贵的眼霜」是自我安慰，规律作息才是唯一解。",
     ["熬夜后怎么补救", "熬夜第二天怎么恢复", "补觉有用吗",
      "熬夜后咖啡因", "长期熬夜的危害"],
     ["问睡眠卫生（用睡眠卡）", "问睡眠呼吸暂停（用打鼾卡）"],
     "atomic", "",
     "熬夜补救=次日自然醒+午后小睡 20-30 分钟（别睡一下午乱节律）+多水高蛋白早餐+白天晒太阳重置生物钟+晚上正常时间睡+咖啡因下午 2 点后停；伤害只能减少不能抵消——规律作息是唯一解。"),
]

QUESTIONS = [
    ("QB-837", "护肤品的正确使用顺序是什么？防晒应该放在哪一步？", "生活常识", "技术直答",
     ["洁面", "化妆水", "精华", "乳液", "防晒", "最后"], "通识拓展206"),
    ("QB-838", "熬夜后第二天应该怎么科学补救？咖啡因什么时候就不能再喝了？", "生活常识", "技术直答",
     ["补觉", "小睡", "30分钟", "蛋白质", "下午", "咖啡因"], "通识拓展206"),
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


def patch_triggers() -> None:
    """短触发复测二缺口：athletesfoot/acnecare 卡补口语短触发词。"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    patches = {
        "kp_card_athletesfoot": ["脚气怎么治", "脚气用药"],
        "kp_card_acnecare": ["长痘能挤吗", "痘痘能挤吗", "挤痘痘"],
    }
    for nid, extra in patches.items():
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if not row or not isinstance(row[0], str):
            continue
        sa = json.loads(row[0])
        if "comment" in sa and "生效条件" in sa["comment"]:
            old = sa["comment"]["生效条件"]
            for t in extra:
                if t not in old:
                    old = old + [t]
            sa["comment"]["生效条件"] = old
            cur.execute("UPDATE nodes SET state_attributes=? WHERE id=?",
                        (json.dumps(sa, ensure_ascii=False), nid))
            print(f"触发词补强: {nid} -> +{extra}")
    conn.commit()
    conn.close()


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
                               "level:L2", "status:verified", "batch:通识拓展206"],
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
    bank["version"] = "v4.78"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
    patch_triggers()
    print("触发词补强完成")
