# -*- coding: utf-8 -*-
"""seed_common_180_cards.py · 通识拓展批次180知识卡+题库（幂等·两卡精批次）

180：生活常识-选购酱油看氨基酸态氮/生活常识-辣椒与解辣
KCCS 四要素+题干原句触发词。三重预检：酱油选购（发酵卡仅列举）与辣椒解辣
双库主题未覆盖；七步洗手命中 epidemic 卡弃选。执行前外文长词检测。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_soyselection",
     "选购酱油看什么",
     "生活常识知识点内容（人话接口）", "生活常识",
     "一瓶酱油好不好，看三处：①**酿造 vs 配制**——瓶身标「酿造酱油」（大豆/"
     "小麦发酵数月，风味物质丰富）优于「配制酱油」（部分酸水解植物蛋白调配，"
     "国家标准要求标注）；②**氨基酸态氮**=鲜味与品质分级核心指标（≥0.80g/"
     "100ml 为特级、≥0.70 一级、≥0.55 二级、≥0.40 三级）——数值越高越鲜；③"
     "**老抽 vs 生抽**——生抽调味提鲜（炒菜凉拌）、老抽加焦糖色上色（红烧卤"
     "味）。**附加**：看配料表首位是水+大豆/脱脂大豆（「零添加」产品其实也含"
     "天然防腐成分如酒精；按需选择即可）；钠含量普遍很高（每 10ml≈1.5-2g "
     "盐）——控盐人群「薄盐酱油」也要看总量；开封后建议冷藏防霉（低盐产品尤"
     "其）。",
     ["怎么选购酱油", "氨基酸态氮是什么", "生抽和老抽的区别",
      "酿造酱油和配制酱油", "酱油分级标准", "薄盐酱油"],
     ["问食品标签（用标签卡）", "问味精安全（用发酵卡）"],
     "atomic", "",
     "选购酱油=酿造优于配制+氨基酸态氮分级(≥0.80 特级/0.70 一级/0.55 二级/0.40 三级，越高越鲜)+生抽调味老抽上色；配料表首位水+大豆；钠含量高控盐看总量；开封冷藏防霉。"),
    ("kp_card_chilispice",
     "辣椒为什么辣，怎么解辣",
     "基础科学知识点内容（人话接口）", "化学",
     "「辣」不是味觉，是**痛觉+热觉**：①辣椒素（capsaicin）激活舌头上的**"
     "TRPV1 受体**（本该感知「高温烫」的受体）——大脑收到「被烫」信号，所以"
     "吃辣会出汗、脸红、流涕；②**解辣要靠脂溶性**：辣椒素**不溶于水**，喝冰"
     "水只能暂时「冲」一下，很快又辣回来；**牛奶/酸奶**中的酪蛋白能**包裹并"
     "带走**辣椒素（解辣最有效）；糖水/含糖饮料也有一定缓解；③**切辣椒辣手"
     "**：辣椒素可经皮肤吸收，戴手套或切前手涂一层油（辣椒素脂溶，油层先占"
     "住受体）；辣手了用**食用油搓手再洗手**，比光用水有效；勿揉眼睛！④**"
     "相对辣度**：史高维尔指标（SHU）——甜椒 0、 墨西哥哈拉帕辣椒数千、朝天椒数万、"
     "世界最辣辣椒超百万（纯辣椒素 1600 万 SHU，警察辣椒喷雾 200-500 万）。",
     ["辣椒为什么辣", "喝牛奶解辣", "切辣椒辣手怎么办",
      "辣椒素是什么", "史高维尔指标", "辣是味觉还是痛觉"],
     ["问美拉德反应（用美拉德卡）", "问肠胃敏感人群饮食"],
     "atomic", "",
     "辣=辣椒素激活 TRPV1 热觉受体的痛觉（非味觉）；解辣靠脂溶性=牛奶酪蛋白包裹带走最有效，水只暂缓；辣手=食用油搓再洗勿揉眼；SHU 辣度=甜椒 0/朝天椒数万/纯辣椒素 1600 万。"),
]

QUESTIONS = [
    ("QB-787", "选购酱油时「氨基酸态氮」指标代表什么？生抽和老抽分别适合做什么？", "生活常识", "技术直答",
     ["氨基酸态氮", "鲜味", "分级", "特级", "生抽调味", "老抽上色"], "通识拓展180"),
    ("QB-788", "吃辣为什么喝冰水没用、喝牛奶才解辣？切辣椒辣手了应该怎么办？", "化学", "技术直答",
     ["辣椒素", "脂溶", "不溶于水", "牛奶", "酪蛋白", "食用油"], "通识拓展180"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词。"""
    whitelist = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
                 "effect", "Additives", "capsaicin", "TRPV1", "SHU",
                 "Jalapeo", "HavillandX"}
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
                               "level:L2", "status:verified", "batch:通识拓展180"],
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
    bank["version"] = "v4.53"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
