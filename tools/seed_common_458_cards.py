# -*- coding: utf-8 -*-
"""seed_common_458_cards.py · 通识拓展批次458知识卡+题库（幂等）

458：2 张存量卡补题（内力与截面法 kp_2821557301 / 自然地理差异性
    kp_3067991317，已在库）+ 1 张新卡（3D打印 kp_card_3dprint，双零）。
预检已过（QB-1609~1611 可用，三主题精确关键词 0 覆盖）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_3dprint",
     "3D打印",
     "前沿科技知识点内容（人话接口）", "科学技术",
     "3D打印（增材制造）——层层「长」出物体的制造方式：①**原理**——把"
     "数字三维模型切成上千个薄层，打印机逐层堆积材料（塑料熔融挤压/"
     "金属粉末激光烧结/光敏树脂紫外固化），与传统「减材」（切削去掉"
     "多余）和「等材」（模具铸造）相反；②**优势**——无需开模，复杂"
     "镂空结构一体成型，个性化定制成本几乎为零（义齿/牙套/助听器"
     "外壳量身定做）；③**应用**——医疗（假体/器官支架研究）、航空"
     "航天（轻量化一体零件）、建筑（打印房屋）、文创手办；④**局限**"
     "——打印速度慢、材料种类有限、大件强度与传统工艺仍有差距；⑤**"
     "趋势**——生物打印（活细胞「打印」组织）是前沿方向。",
     ["3D打印是什么原理", "增材制造", "3D打印能打印什么",
      "3D打印的优势", "生物打印", "3D打印和传统制造区别"],
     ["问机器人", "问智能制造"],
     "atomic", "",
     "3D打印=增材制造数字模型切片逐层堆积与减材等材相反+塑料熔融金属"
     "粉末激光烧结光敏树脂固化+无需开模复杂镂空一体成型个性定制零成"
     "本+义齿牙套假体航空航天轻量化建筑房屋+速度慢材料受限+生物打印"
     "活细胞组织是前沿。"),
]

QUESTIONS = [
    ("QB-1609", "什么是截面法？轴力、剪力、弯矩分别指什么？",
     "工程力学", "技术直答",
     ["截面法", "内力", "轴力", "弯矩"], "通识拓展458·存量卡补题"),
    ("QB-1610", "自然地理环境的差异性有哪些分异规律？",
     "地理常识", "技术直答",
     ["差异性", "纬度地带性", "经度地带性", "垂直地带性"], "通识拓展458·存量卡补题"),
    ("QB-1611", "3D打印的原理是什么？它有哪些应用？",
     "科学技术", "技术直答",
     ["3D打印", "增材制造", "逐层", "定制"], "通识拓展458"),
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
                               "level:L2", "status:verified", "batch:通识拓展458"],
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
    bank["version"] = "v7.28"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
