# -*- coding: utf-8 -*-
"""seed_common_282_cards.py · 通识拓展批次282知识卡+题库（幂等）

282：物理-冰刀为什么能滑/物理-润滑剂为什么能减摩擦（冰雪润滑新域）
KCCS 四要素+题干原句触发词。预检已过（QB-1069/1070+双id可用）。
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
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA"}


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
    ("kp_card_iceskate",
     "冰刀为什么能滑",
     "物理通识知识点内容（人话接口）", "基础科学",
     "冰面为什么特别滑：①**压强熔化假说**——冰刀窄刃面积小，人体重量压出"
     "巨大压强，冰的熔点随压强升高而降低，接触面微熔出一层水膜充当「自"
     "润滑」——压强越集中越滑（穿窄冰刀 vs 平底鞋差很多）；②**摩擦生热"
     "假说（补充）**——滑动摩擦产生的热也维持水膜，静止时压强效应仍让"
     "冰面有准液态层——两个机制共同作用，现代研究认为摩擦热贡献更大；③"
     "**冰的表面本性**——即使 -10°C 冰表面也存在准液态分子层（表面分子"
     "无配对「悬空键」），这是冰本身滑的基础；④**冰刀设计**——弧形刃"
     "（利于转弯压步）、开槽刃（两棱切冰转向抓冰）、花刀多齿（起跳点冰）；"
     "⑤**温度影响**——过冷（-20°C 以下）冰面太硬水膜少反而难滑涩，-5°C"
     " 附近最理想，室内冰场约 -5~-7°C。",
     ["冰面为什么滑", "冰刀的原理", "冰上滑行是什么原理",
      "冰刀刃为什么是弧的", "冰面下温度多少最好滑", "压强使冰熔化"],
     ["问速滑技术", "问造冰工艺"],
     "atomic", "",
     "冰刀=窄刃压强大冰熔点降低微熔水膜自润滑+摩擦生热共同维持+冰表面"
     "本有准液态层(悬空键)+弧形开槽刃设计+过冷太硬难滑-5°C最理想。"),
    ("kp_card_lubricate",
     "润滑剂为什么能减摩擦",
     "物理通识知识点内容（人话接口）", "基础科学",
     "润滑的科学：①**基本原理**——在两摩擦面之间塞进一层易剪切的介质，"
     "把「干摩擦」（固对固）换成「流体摩擦」（液体内部分子间滑动）——"
     "流体摩擦系数小一到两个数量级；②**油膜厚度三态**——流体润滑（油膜"
     "完全隔开两面最理想）/边界润滑（油膜薄到只剩分子层，靠添加剂分子"
     "「站」在表面）/混合润滑（时开时合，最常见工况——启动停车瞬间磨损"
     "最大）；③**机油的角色**——除了减摩还带走热量（冷却）+冲走磨屑"
     "（清洁）+防锈密封；粘度是关键指标（低温要能流动高温要保持油膜，"
     "多级机油如 5W-30 兼顾）；④**固体润滑**——石墨/二硫化钼层状结构"
     "层间易滑（铅笔芯润滑、高温场合油会烧掉只能用固体）；⑤**生物润滑**"
     "——关节滑液（透明质酸）摩擦系数低到 0.001 级，比任何人造轴承都强；"
     "⑥**勿混用**——不同油品添加剂可能反应失效。",
     ["润滑剂为什么能减少摩擦", "机油起什么作用", "机油标号什么意思",
      "石墨为什么能当润滑剂", "关节为什么那么灵活", "流体润滑"],
     ["问润滑油添加剂", "问磁悬浮轴承"],
     "atomic", "",
     "润滑=易剪切介质把干摩擦换流体摩擦降一两个数量级+三态(流体/边界/"
     "混合·启停磨损最大)+机油减摩冷却清洁防锈+粘度标号兼顾冷热+石墨二硫"
     "化钼层状固体润滑耐高温+关节滑液0.001级生物冠军。"),
]

QUESTIONS = [
    ("QB-1069", "冰面为什么特别滑？冰刀是怎么设计的？", "基础科学", "技术直答",
     ["压强", "水膜", "熔化", "冰刀"], "通识拓展282"),
    ("QB-1070", "润滑剂为什么能减少摩擦？机油有哪些作用？", "基础科学", "技术直答",
     ["油膜", "流体", "粘度", "冷却"], "通识拓展282"),
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
                               "level:L2", "status:verified", "batch:通识拓展282"],
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
                   "added": "2026-09-06"})
        added += 1
    bank["version"] = "v5.53"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
