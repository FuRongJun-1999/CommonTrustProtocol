# -*- coding: utf-8 -*-
"""seed_common_198_cards.py · 通识拓展批次198知识卡+题库（幂等·两卡精批次）

198：生活常识-腹泻时的正确补水/生活常识-干眼与人工泪液
KCCS 四要素+题干原句触发词。三重预检：腹泻补液（sweeteners/lactobacillus
卡仅诱因角度）与干眼护理（eyelid 卡仅诱因角度）主题均未覆盖。
执行前外文长词检测（CPAP 等白名单沿用）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_diarrheahydration",
     "腹泻时最要紧的是补水",
     "生活常识知识点内容（人话接口）", "生活常识",
     "腹泻最危险的不是「拉」本身，而是**脱水和电解质紊乱**（尤其儿童老人）。**"
     "核心对策=补液**：①**口服补液盐 III**（药店有售，按说明冲调）——成分配"
     "比（葡萄糖+钠钾）专为肠道最优吸收设计，比白水管用得多；②自制应急：温"
     "开水+少量盐+糖（不如补液盐标准，应急可用）；③**喝白水不够**——只补水"
     "不补电解质会稀释血钠（低钠更难受）。**止泻药慎用**：感染性腹泻早期强行"
     "止泻可能把毒素/病原「憋」在肠道里（发热加重）——先补液观察，高热脓血"
     "便就医查因。**饮食**：清淡（粥/面条）、避高糖饮料（渗透性加重腹泻——"
     "包括果汁与含糖汽水）、避奶制品（暂时乳糖不耐）。**就医线**：持续超过 2"
     " 天、高热、脓血便、严重口渴尿少（脱水征）、儿童老人精神差。",
     ["拉肚子要吃什么", "腹泻为什么喝补液盐", "腹泻能不能吃止泻药",
      "腹泻脱水症状", "口服补液盐", "拉肚子能喝果汁吗"],
     ["问诺如病毒防护", "问益生菌选择"],
     "atomic", "",
     "腹泻最险=脱水+电解质紊乱（儿童老人尤甚）：核心=口服补液盐 III（配比优于白水）；止泻药慎用（感染早期憋毒加重）；饮食清淡避高糖果汁（渗透性加重）；就医线=超 2 天/高热/脓血便/脱水征/精神差。"),
    ("kp_card_dryeyecare",
     "干眼与人工泪液",
     "生活常识知识点内容（人话接口）", "生活常识",
     "干眼=泪液**分泌不足或蒸发过快**（睑板腺功能障碍为主因），症状=干涩/异"
     "物感/灼烧/视疲劳波动。**护理**：①**有意识多眨眼**（盯屏时眨眼次数骤降"
     "一半以上）；②**20-20-20 法则**——每 20 分钟看 20 英尺（6 米）外 20 秒；"
     "③**人工泪液**——首选**不含防腐剂**的单支装（长期用含苯扎氯铵的眼药水"
     "反伤眼表）；「网红眼药水」（清凉感/快速去红血丝）多含收缩血管剂，越用"
     "越依赖——**别当日常保健用**；④热敷（睑板腺疏通）+加湿器；⑤严重的干眼"
     "是慢性病，需眼科分型治疗。屏幕亮度与环境光匹配、屏幕略低于视线（减少"
     "睑裂暴露）也有效。",
     ["眼睛干涩怎么办", "人工泪液怎么选", "网红眼药水能长期用吗",
      "20-20-20法则", "干眼症护理"],
     ["问睑板腺按摩（就医）", "问近视防控（用近视卡）"],
     "atomic", "",
     "干眼=泪液分泌不足或蒸发过快（睑板腺障碍为主）：护理=有意识眨眼+20-20-20+不含防腐剂单支人工泪液+热敷；网红眼药水含血管收缩剂越用越依赖勿当保健；严重干眼=慢性病眼科分型治疗。"),
]

QUESTIONS = [
    ("QB-824", "拉肚子的时候为什么要优先喝口服补液盐？什么情况下必须就医？", "生活常识", "技术直答",
     ["脱水", "电解质", "补液盐", "止泻", "脓血便", "就医"], "通识拓展198"),
    ("QB-825", "眼睛干涩应该怎么护理？为什么网红眼药水不建议长期用？", "生活常识", "技术直答",
     ["人工泪液", "防腐剂", "20-20-20", "眨眼", "血管收缩"], "通识拓展198"),
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
                               "level:L2", "status:verified", "batch:通识拓展198"],
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
    bank["version"] = "v4.71"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
