# -*- coding: utf-8 -*-
"""seed_common_280_cards.py · 通识拓展批次280知识卡+题库（幂等）

280：食品科学-酵母发酵原理/食品科学-膨松剂发面原理
KCCS 四要素+题干原句触发词。预检已过（QB-1062/1063+双id可用）。
注：QB-322/538 是小苏打纯碱化学品区分，本批发面角度避让。
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
             "FADH2", "Vmax", "Km"}


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
    ("kp_card_yeast2",
     "酵母发酵原理",
     "食品科学知识点内容（人话接口）", "生活常识",
     "酵母怎么让面团变大：①**核心=酵母菌吃糖产气**——酵母分解面团中的糖类"
     "（淀粉被酶切成葡萄糖），产生二氧化碳+酒精（发酵），气泡被面筋网络"
     "「兜住」出不来，面团就膨大松软（面包孔洞就是气泡遗迹）；②**适宜条件**"
     "——温度 28-32°C 最活跃（过热 >60°C 烫死酵母）、有水、有糖更旺（加糖"
     "发得快但过量反而抑制渗透压失水）；③**发酵过头**——酸味重（杂菌产酸"
     "）气泡粗大气孔塌陷——闻着发酸组织粗糙即发过头；④**盐的角色**——"
     "少量盐增强面筋支撑+抑制酵母过快发酵（后盐法），无盐面团发得快但"
     "结构松散没嚼劲；⑤**馒头包子 vs 面包**——原理同为酵母产气，面包多"
     "油糖二次发酵烤制，馒头蒸制（蒸汽加热定型，温度不过百不褐变，所以"
     "白净无壳）；⑥**老面/酵头**——天然混合菌群发酵带微酸风味，需加碱"
     "中和（老面馒头的碱香）。",
     ["酵母发酵的原理", "面团为什么发起来", "发面水温多少合适",
      "面团发酵过头了怎么办", "盐对面团有什么用", "老面馒头为什么要加碱"],
     ["问酵母菌种选育", "问酸面团工艺"],
     "atomic", "",
     "酵母发酵=酵母分解糖产CO₂与酒精被面筋网络兜住膨大(孔洞=气泡遗迹)+"
     "28-32°C最适过热烫死+糖催旺过量抑制+发过头酸味塌陷+盐壮面筋抑菌"
     "后盐法+馒头蒸制无褐变白净+老面菌群需加碱中和。"),
    ("kp_card_baking",
     "膨松剂发面原理",
     "食品科学知识点内容（人话接口）", "生活常识",
     "膨松剂怎么让糕点松软：①**化学膨松剂路线**——小苏打（碳酸氢钠）受热"
     "分解产二氧化碳；泡打粉=小苏打+酸性盐（塔塔粉/磷酸盐）双组分遇水湿"
     "即反应产气，无需发酵时间；②**酵母 vs 泡打粉**——酵母生物发酵慢但"
     "风味足（产酒精与风味物），泡打粉快但风味单一，两者可并用（面包靠"
     "酵母、蛋糕饼干多靠泡打粉）；③**使用要点**——小苏打单用产气不足且"
     "残留碱性（发黄发苦味），配酸性材料（酸奶/可可粉）才好用；泡打粉勿"
     "过量（碱味+组织粗糙）；④**物理膨松**——打发鸡蛋（蛋清打发裹入空气"
     "戚风蛋糕）、蒸汽（泡芙水蒸气膨胀）、油脂起酥分层（开酥）——不靠菌"
     "不靠药全靠物理；⑤**油条的秘密**——传统「矾碱盐」膨松（铝隐患被"
     "无铝配方替代），两片叠压高温油炸瞬间产气膨胀。",
     ["泡打粉和小苏打有什么区别", "膨松剂是什么原理", "蛋糕为什么蓬松",
      "油条为什么中间空心", "泡打粉放多了会怎样", "化学膨松剂"],
     ["问无铝油条配方", "问蛋糕打发技巧"],
     "atomic", "",
     "膨松剂=化学(小苏打受热产气/泡打粉双组分遇水即产气)+生物(酵母慢但"
     "风味足)两路线+小苏打单用残留碱性发苦配酸才好+物理膨松(打蛋裹气/"
     "蒸汽/油脂起酥)+油条矾碱盐现无铝配方。"),
]

QUESTIONS = [
    ("QB-1062", "酵母是怎么让面团发起来的？面团发酵过头了会怎样？", "生活常识", "技术直答",
     ["酵母", "二氧化碳", "面筋", "发酸"], "通识拓展280"),
    ("QB-1063", "泡打粉和小苏打有什么区别？蛋糕的蓬松靠什么？", "生活常识", "技术直答",
     ["泡打粉", "小苏打", "产气", "打发"], "通识拓展280"),
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
                               "level:L2", "status:verified", "batch:通识拓展280"],
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
    bank["version"] = "v5.51"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
